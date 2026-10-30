import uuid

from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from contemplart.accounts.models import Customer
from contemplart.catalog.models import Product


# ClusterableModel/ParentalKey permitem editar os itens dentro da tela do
# pedido no painel (Wagtail InlinePanel); no banco continua sendo uma FK.
class Order(ClusterableModel):
    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pendente'),
        (PAID, 'Pago'),
        (SHIPPED, 'Enviado'),
        (COMPLETED, 'Concluído'),
        (CANCELLED, 'Cancelado'),
    ]
    # Status em que o pagamento já foi recebido.
    STATUS_PAGOS = (PAID, SHIPPED, COMPLETED)

    # TODO(Fase 2): endereco_entrega deveria ser FK para um model Address,
    # que ainda não está definido em DATA_MODEL.md. Usando texto livre
    # como placeholder até essa decisão ser tomada.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='pedidos')
    email_cliente = models.EmailField('e-mail do cliente', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    endereco_entrega = models.TextField('endereço de entrega', null=True, blank=True)
    valor_frete = models.DecimalField('frete', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Data em que a venda aconteceu (pode diferir de criado_em em vendas
    # importadas); nula quando desconhecida.
    data_venda = models.DateField('data da venda', null=True, blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        ordering = ['-criado_em']

    def __str__(self):
        data = self.data_venda or (self.criado_em and self.criado_em.date())
        return f'Pedido de {self.cliente}' + (f' em {data:%d/%m/%Y}' if data else '')


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = ParentalKey(Order, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='itens_pedido')
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(
        'preço unitário', max_digits=10, decimal_places=2, blank=True,
        help_text='Deixe vazio para usar o preço do produto (varejo ou atacado, conforme o cliente).',
    )

    class Meta:
        verbose_name = 'item do pedido'
        verbose_name_plural = 'itens do pedido'

    def save(self, *args, **kwargs):
        if self.preco_unitario is None:
            from .services import preco_efetivo
            self.preco_unitario = preco_efetivo(self.produto, self.pedido.cliente)
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return (self.preco_unitario or 0) * self.quantidade

    def __str__(self):
        return f'{self.quantidade}x {self.produto}'

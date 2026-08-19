import uuid

from django.db import models

from contemplart.accounts.models import Customer


class Order(models.Model):
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

    # TODO(Fase 2): endereco_entrega deveria ser FK para um model Address,
    # que ainda não está definido em DATA_MODEL.md. Usando texto livre
    # como placeholder até essa decisão ser tomada.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='pedidos')
    email_cliente = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    endereco_entrega = models.TextField(null=True, blank=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido {self.id} ({self.status})'

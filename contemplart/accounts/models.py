import uuid

from django.conf import settings
from django.db import models


class Customer(models.Model):
    RETAIL = 'retail'
    WHOLESALE = 'wholesale'
    CUSTOMER_TYPE_CHOICES = [
        (RETAIL, 'Varejo'),
        (WHOLESALE, 'Atacado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Nulo para clientes cadastrados pela equipe no painel, que não fazem
    # login na loja; quem se cadastra na loja tem usuário.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    nome = models.CharField(max_length=255)
    email = models.EmailField('e-mail', blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    endereco = models.TextField('endereço', blank=True)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=20, blank=True)
    pessoa_contato = models.CharField('pessoa de contato', max_length=255, blank=True)
    tipo_cliente = models.CharField('tipo de cliente', max_length=20, choices=CUSTOMER_TYPE_CHOICES, default=RETAIL)
    observacoes = models.TextField('observações', blank=True)
    criado_em = models.DateTimeField('cadastrado em', auto_now_add=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

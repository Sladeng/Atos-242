import uuid

from django.db import models

from contemplart.orders.models import Order


class AccountPayable(models.Model):
    INSUMO = 'insumo'
    FRETE = 'frete'
    TAXA_GATEWAY = 'taxa_gateway'
    OUTRO = 'outro'
    CATEGORY_CHOICES = [
        (INSUMO, 'Insumo'),
        (FRETE, 'Frete'),
        (TAXA_GATEWAY, 'Taxa de gateway'),
        (OUTRO, 'Outro'),
    ]

    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (PENDING, 'Pendente'),
        (PAID, 'Pago'),
        (OVERDUE, 'Vencido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descricao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    pago_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.descricao


class AccountReceivable(models.Model):
    PENDING = 'pending'
    RECEIVED = 'received'
    OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (PENDING, 'Pendente'),
        (RECEIVED, 'Recebido'),
        (OVERDUE, 'Vencido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='contas_a_receber', null=True, blank=True
    )
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    recebido_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.descricao

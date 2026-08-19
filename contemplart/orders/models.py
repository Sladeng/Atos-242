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

    # TODO(Fase 2): shipping_address deveria ser FK para um model Address,
    # que ainda não está definido em DATA_MODEL.md. Usando texto livre
    # como placeholder até essa decisão ser tomada.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    shipping_address = models.TextField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} ({self.status})'

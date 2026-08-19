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
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=30, blank=True)
    tipo_cliente = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default=RETAIL)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

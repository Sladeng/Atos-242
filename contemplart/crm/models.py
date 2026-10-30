import uuid

from django.db import models

from contemplart.accounts.models import Customer


class Interaction(models.Model):
    CALL = 'call'
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'
    MEETING = 'meeting'
    TYPE_CHOICES = [
        (CALL, 'Ligação'),
        (EMAIL, 'E-mail'),
        (WHATSAPP, 'WhatsApp'),
        (MEETING, 'Reunião'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interacoes')
    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES)
    observacoes = models.TextField('observações', blank=True)
    data = models.DateTimeField()
    data_retorno = models.DateTimeField('retornar em', null=True, blank=True)

    class Meta:
        verbose_name = 'interação'
        verbose_name_plural = 'interações'
        ordering = ['-data']

    def __str__(self):
        return f'{self.get_tipo_display()} com {self.cliente} em {self.data:%d/%m/%Y}'

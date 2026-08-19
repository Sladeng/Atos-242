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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    notes = models.TextField(blank=True)
    date = models.DateTimeField()
    follow_up_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.get_type_display()} com {self.customer} em {self.date:%d/%m/%Y}'

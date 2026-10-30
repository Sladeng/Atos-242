from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from contemplart.orders.models import Order

from .models import AccountReceivable


@receiver(post_save, sender=Order)
def pedido_pago_gera_conta_a_receber(sender, instance, **kwargs):
    """Pedido pago gera uma AccountReceivable (RULES.md → Financeiro).

    Chave por pedido: salvar de novo só atualiza o valor, nunca duplica.
    Status/data de recebimento definidos na criação não são sobrescritos.
    """
    if instance.status not in Order.STATUS_PAGOS:
        return
    agora = timezone.now()
    AccountReceivable.objects.update_or_create(
        pedido=instance,
        defaults={'valor': instance.total},
        create_defaults={
            'valor': instance.total,
            'descricao': f'Venda - {instance.cliente}',
            'data_vencimento': instance.data_venda or timezone.localdate(),
            'status': AccountReceivable.RECEIVED,
            'recebido_em': agora,
        },
    )

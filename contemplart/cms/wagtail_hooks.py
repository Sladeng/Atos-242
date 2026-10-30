from datetime import datetime

from django.db.models import Q, Sum
from django.urls import reverse
from django.utils import timezone
from wagtail import hooks
from wagtail.admin.ui.components import Component

from contemplart.finance.models import AccountPayable, AccountReceivable
from contemplart.orders.models import Order


class ResumoPanel(Component):
    """Resumo da operação na tela inicial do painel (somente leitura)."""

    name = 'resumo'
    order = 50
    template_name = 'cms/painel_resumo.html'

    def __init__(self, user):
        self.user = user

    def get_context_data(self, parent_context):
        hoje = timezone.localdate()
        inicio_mes = hoje.replace(day=1)
        inicio_mes_dt = timezone.make_aware(datetime.combine(inicio_mes, datetime.min.time()))

        pendentes = Order.objects.filter(status=Order.PENDING).select_related('cliente')
        vendas_mes = Order.objects.filter(status__in=Order.STATUS_PAGOS).filter(
            Q(data_venda__gte=inicio_mes) | Q(data_venda__isnull=True, criado_em__gte=inicio_mes_dt)
        )
        contexto = {
            'pedidos_pendentes': pendentes.count(),
            'ultimos_pendentes': pendentes.order_by('-criado_em')[:5],
            'vendas_mes': vendas_mes.aggregate(t=Sum('total'))['t'] or 0,
            'mes': hoje,
            'url_pedidos': reverse('order:index'),
            'url_novo_pedido': reverse('order:add'),
            'ver_financeiro': self.user.has_perm('finance.view_accountreceivable'),
        }
        if contexto['ver_financeiro']:
            vencidas = AccountPayable.objects.filter(status=AccountPayable.PENDING, data_vencimento__lt=hoje)
            contexto.update({
                'a_receber': AccountReceivable.objects.exclude(status=AccountReceivable.RECEIVED)
                .aggregate(t=Sum('valor'))['t'] or 0,
                'contas_vencidas': vencidas.count(),
                'valor_vencido': vencidas.aggregate(t=Sum('valor'))['t'] or 0,
            })
        return contexto


@hooks.register('construct_homepage_panels')
def adicionar_resumo(request, panels):
    panels.insert(0, ResumoPanel(request.user))

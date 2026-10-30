from wagtail import hooks
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.viewsets.model import ModelViewSet

from .models import AccountPayable, AccountReceivable


class AccountReceivableViewSet(ModelViewSet):
    model = AccountReceivable
    icon = 'success'
    menu_label = 'Contas a receber'
    list_display = ['descricao', 'valor', 'data_vencimento', 'status', 'recebido_em']
    list_filter = ['status']
    search_fields = ['descricao']
    search_backend_name = None
    panels = [
        FieldPanel('descricao'),
        FieldRowPanel([FieldPanel('valor'), FieldPanel('data_vencimento')]),
        FieldRowPanel([FieldPanel('status'), FieldPanel('recebido_em')]),
        FieldPanel('pedido', read_only=True),
    ]


class AccountPayableViewSet(ModelViewSet):
    model = AccountPayable
    icon = 'warning'
    menu_label = 'Contas a pagar'
    list_display = ['descricao', 'categoria', 'valor', 'data_vencimento', 'status']
    list_filter = ['status', 'categoria']
    search_fields = ['descricao']
    search_backend_name = None
    panels = [
        FieldRowPanel([FieldPanel('descricao'), FieldPanel('categoria')]),
        FieldRowPanel([FieldPanel('valor'), FieldPanel('data_vencimento')]),
        FieldRowPanel([FieldPanel('status'), FieldPanel('pago_em')]),
    ]


class FinanceiroGroup(ViewSetGroup):
    menu_label = 'Financeiro'
    menu_icon = 'doc-full'
    menu_order = 120
    items = (AccountReceivableViewSet, AccountPayableViewSet)


@hooks.register('register_admin_viewset')
def registrar_financeiro():
    return FinanceiroGroup()

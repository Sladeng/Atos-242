from wagtail import hooks
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.viewsets.model import ModelViewSet

from contemplart.crm.models import Interaction

from .models import Customer


class CustomerViewSet(ModelViewSet):
    model = Customer
    icon = 'group'
    menu_label = 'Clientes'
    list_display = ['nome', 'tipo_cliente', 'telefone', 'pessoa_contato', 'email']
    list_filter = ['tipo_cliente']
    search_fields = ['nome', 'email', 'telefone', 'cpf_cnpj', 'pessoa_contato']
    search_backend_name = None
    panels = [
        FieldRowPanel([FieldPanel('nome'), FieldPanel('tipo_cliente')]),
        FieldRowPanel([FieldPanel('telefone'), FieldPanel('email')]),
        FieldRowPanel([FieldPanel('pessoa_contato'), FieldPanel('cpf_cnpj')]),
        FieldPanel('endereco'),
        FieldPanel('observacoes'),
    ]


class InteractionViewSet(ModelViewSet):
    model = Interaction
    icon = 'mail'
    menu_label = 'Interações'
    list_display = ['cliente', 'tipo', 'data', 'data_retorno']
    list_filter = ['tipo', 'cliente']
    search_fields = ['cliente__nome', 'observacoes']
    search_backend_name = None
    panels = [
        FieldRowPanel([FieldPanel('cliente'), FieldPanel('tipo')]),
        FieldRowPanel([FieldPanel('data'), FieldPanel('data_retorno')]),
        FieldPanel('observacoes'),
    ]


class ClientesGroup(ViewSetGroup):
    menu_label = 'Clientes'
    menu_icon = 'group'
    menu_order = 110
    items = (CustomerViewSet, InteractionViewSet)


@hooks.register('register_admin_viewset')
def registrar_clientes():
    return ClientesGroup()

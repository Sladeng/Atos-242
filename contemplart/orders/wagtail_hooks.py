from wagtail import hooks
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, ObjectList
from wagtail.admin.viewsets.model import ModelViewSet

from .forms import PedidoForm
from .models import Order


class OrderViewSet(ModelViewSet):
    model = Order
    icon = 'clipboard-list'
    menu_label = 'Pedidos'
    menu_order = 90
    add_to_admin_menu = True
    list_display = ['cliente', 'status', 'total', 'data_venda', 'criado_em']
    list_filter = ['status', 'cliente']
    search_fields = ['cliente__nome', 'email_cliente']
    search_backend_name = None
    copy_view_enabled = False
    edit_handler = ObjectList(
        [
            FieldRowPanel([FieldPanel('cliente'), FieldPanel('status'), FieldPanel('data_venda')]),
            InlinePanel('itens', heading='Itens', label='item', min_num=1),
            FieldRowPanel([FieldPanel('valor_frete'), FieldPanel('total', read_only=True)]),
            FieldPanel('endereco_entrega'),
            FieldPanel('email_cliente'),
        ],
        base_form_class=PedidoForm,
    )


@hooks.register('register_admin_viewset')
def registrar_pedidos():
    return OrderViewSet()

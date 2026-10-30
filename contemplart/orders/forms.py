from wagtail.admin.forms import WagtailAdminModelForm

from .services import recalcular_total


class PedidoForm(WagtailAdminModelForm):
    def save(self, commit=True):
        pedido = self.instance
        if not pedido.email_cliente and pedido.cliente_id:
            pedido.email_cliente = pedido.cliente.email
        pedido = super().save(commit=commit)
        if commit:
            recalcular_total(pedido)
        return pedido

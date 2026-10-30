from decimal import Decimal

from contemplart.accounts.models import Customer


def preco_efetivo(produto, cliente):
    """Preço de um produto para um cliente (DATA_MODEL.md → Regras derivadas).

    Variações (`ProductVariant.preco_personalizado`) ainda não existem.
    """
    if cliente.tipo_cliente == Customer.WHOLESALE and produto.preco_atacado is not None:
        return produto.preco_atacado
    return produto.preco


def recalcular_total(pedido):
    """Total = soma dos itens + frete. Pedido sem itens mantém o total atual."""
    itens = list(pedido.itens.all())
    if not itens:
        return pedido.total
    total = sum((item.subtotal for item in itens), Decimal('0')) + (pedido.valor_frete or 0)
    if total != pedido.total:
        pedido.total = total
        pedido.save(update_fields=['total'])
    return total

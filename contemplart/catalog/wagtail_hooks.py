from wagtail import hooks
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Category, Product


class ProductViewSet(ModelViewSet):
    model = Product
    icon = 'tag'
    menu_label = 'Produtos'
    list_display = ['nome', 'preco', 'preco_atacado', 'quantidade_estoque', 'ativo']
    list_filter = ['ativo', 'categoria', 'material']
    search_fields = ['nome', 'descricao']
    search_backend_name = None
    panels = [
        FieldPanel('nome'),
        FieldRowPanel([FieldPanel('preco'), FieldPanel('preco_atacado')], heading='Preços'),
        FieldRowPanel([FieldPanel('categoria'), FieldPanel('material'), FieldPanel('tipo_produto')]),
        FieldRowPanel([FieldPanel('quantidade_estoque'), FieldPanel('ativo')]),
        FieldPanel('descricao'),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel('custo'), FieldPanel('peso_g'), FieldPanel('tempo_impressao')]),
                FieldPanel('slug'),
            ],
            heading='Produção e detalhes',
            classname='collapsed',
        ),
    ]


class CategoryViewSet(ModelViewSet):
    model = Category
    icon = 'folder-open-1'
    menu_label = 'Categorias'
    list_display = ['nome']
    search_fields = ['nome']
    search_backend_name = None
    panels = [FieldPanel('nome'), FieldPanel('slug')]


class CatalogoGroup(ViewSetGroup):
    menu_label = 'Catálogo'
    menu_icon = 'tag'
    menu_order = 100
    items = (ProductViewSet, CategoryViewSet)


@hooks.register('register_admin_viewset')
def registrar_catalogo():
    return CatalogoGroup()

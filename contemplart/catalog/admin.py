from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_produto', 'preco', 'preco_atacado', 'quantidade_estoque', 'ativo')
    list_filter = ('tipo_produto', 'material', 'ativo', 'categoria')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)

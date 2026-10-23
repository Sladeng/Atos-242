from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ('produto',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'total', 'data_venda', 'criado_em')
    list_filter = ('status',)
    search_fields = ('email_cliente', 'cliente__nome')
    inlines = [OrderItemInline]

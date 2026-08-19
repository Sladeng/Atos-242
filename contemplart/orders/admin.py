from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'total', 'criado_em')
    list_filter = ('status',)
    search_fields = ('email_cliente',)

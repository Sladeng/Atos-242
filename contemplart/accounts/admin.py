from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_cliente', 'criado_em')
    list_filter = ('tipo_cliente',)
    search_fields = ('nome', 'email', 'telefone')

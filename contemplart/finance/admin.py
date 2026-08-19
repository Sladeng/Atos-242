from django.contrib import admin

from .models import AccountPayable, AccountReceivable


@admin.register(AccountPayable)
class AccountPayableAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_vencimento', 'status')
    list_filter = ('categoria', 'status')
    search_fields = ('descricao',)


@admin.register(AccountReceivable)
class AccountReceivableAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'pedido', 'valor', 'data_vencimento', 'status')
    list_filter = ('status',)
    search_fields = ('descricao',)

from django.contrib import admin

from .models import AccountPayable, AccountReceivable


@admin.register(AccountPayable)
class AccountPayableAdmin(admin.ModelAdmin):
    list_display = ('description', 'category', 'amount', 'due_date', 'status')
    list_filter = ('category', 'status')
    search_fields = ('description',)


@admin.register(AccountReceivable)
class AccountReceivableAdmin(admin.ModelAdmin):
    list_display = ('description', 'order', 'amount', 'due_date', 'status')
    list_filter = ('status',)
    search_fields = ('description',)

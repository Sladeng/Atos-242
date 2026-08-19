from django.contrib import admin

from .models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'data', 'data_retorno')
    list_filter = ('tipo',)
    search_fields = ('cliente__nome', 'observacoes')

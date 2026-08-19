from django.contrib import admin

from .models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'type', 'date', 'follow_up_date')
    list_filter = ('type',)
    search_fields = ('customer__name', 'notes')

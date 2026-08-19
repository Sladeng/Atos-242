from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'customer_type', 'created_at')
    list_filter = ('customer_type',)
    search_fields = ('name', 'email', 'phone')

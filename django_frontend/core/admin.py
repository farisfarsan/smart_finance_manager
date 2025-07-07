from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'amount', 'date_fetched', 'created_at')
    search_fields = ('user__username', 'platform')
    list_filter = ('platform', 'date_fetched')

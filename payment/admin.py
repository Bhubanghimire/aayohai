from django.contrib import admin
from payment.models import Invoice

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "created_at", "updated_at"]
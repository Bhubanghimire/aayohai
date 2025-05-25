from django.contrib import admin
from payment.models import Invoice, Ticket

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "book", "total_amount", "created_at", "updated_at"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id",]
from django.contrib import admin
from book.models import Cart


# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', "grocery", 'created_at', 'updated_at')


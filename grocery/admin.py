from django.contrib import admin
from grocery.models import Grocery


# Register your models here.
@admin.register(Grocery)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',"quantity_unit",'created_at','updated_at')

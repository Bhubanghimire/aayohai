from django.contrib import admin
from grocery.models import Grocery, GroceryCategory, Gallery


# Register your models here.
@admin.register(Grocery)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',"quantity_unit",'created_at','updated_at')

@admin.register(GroceryCategory)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',)

@admin.register(Gallery)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',)


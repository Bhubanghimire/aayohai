from django.contrib import admin
from book.models import Cart, Book, BookItem, RoomDiscount, OrderItem, EventItem, RoomDiscount, GroceryDiscount


# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', "grocery", 'quantity', 'created_at', 'updated_at')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['uuid', "user", "status", "created_at", "updated_at"]


@admin.register(BookItem)
class BookItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'room', 'total_amount', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', "grocery", "created_at", "updated_at"]


@admin.register(EventItem)
class EventItemAdmin(admin.ModelAdmin):
    list_display = ['id', "event", "created_at", "updated_at"]

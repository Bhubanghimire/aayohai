from django.db import models

import uuid
from accounts.models import User
from events.models import Event, EventPrice
from grocery.models import Grocery
from room.models import Room
from system.models import ConfigChoice, SoftDeletable


# Create your models here.
class RoomDiscount(SoftDeletable):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    discount_type = models.ForeignKey(ConfigChoice, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.discount_type)


class GroceryDiscount(SoftDeletable):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    discount_type = models.ForeignKey(ConfigChoice, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.discount_type)


class Book(SoftDeletable):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(ConfigChoice, on_delete=models.CASCADE, null=True, related_name="book_status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class BookItem(SoftDeletable):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, null=True, blank=True)
    discount = models.ForeignKey(RoomDiscount, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField()
    total_amount =models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.room.name} {self.book}'


class Cart(SoftDeletable):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grocery = models.ForeignKey(Grocery, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}'


class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    grocery = models.ForeignKey(Grocery, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    comment = models.CharField(max_length=250, null=True, blank=True)
    discount = models.ForeignKey(RoomDiscount, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField()
    total_amount =models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.grocery.name}'


class EventItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, null=True, blank=True)
    discount = models.ForeignKey(RoomDiscount, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField()
    event_price = models.ForeignKey(EventPrice, on_delete=models.CASCADE, null=True, blank=True)
    count = models.IntegerField(default=1)
    total_amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event.title}'

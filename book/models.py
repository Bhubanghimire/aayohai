from django.db import models

import uuid
from accounts.models import User
from room.models import Room
from system.models import ConfigChoice


# Create your models here.
class RoomDiscount(models.Model):
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


class Book(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(ConfigChoice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class BookItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, null=True, blank=True)
    discount = models.ForeignKey(RoomDiscount, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=17, decimal_places=2)
    total_amount = models.DecimalField(max_digits=17, decimal_places=2)

    def __str__(self):
        return f'{self.room.name} {self.book}'


# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     quantity = models.IntegerField(null=True, blank=True)
#     discount = models.ForeignKey(ProductDiscount, on_delete=models.CASCADE, null=True, blank=True)
#     color = models.ForeignKey(ConfigChoice, on_delete=models.CASCADE)
#     size = models.ForeignKey(ConfigChoice, related_name='cart_product_size', on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#
#     def __str__(self):
#         return f'{self.product.name} {self.order}'
from django.db import models

from accounts.models import User
from system.models import ConfigChoice, SoftDeletable


# Create your models here.
class GroceryCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='grocery/category/')
    status = models.BooleanField(default=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Grocery(SoftDeletable):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cover_image = models.ImageField()
    quantity = models.PositiveIntegerField()
    quantity_unit = models.ForeignKey(ConfigChoice, on_delete=models.CASCADE, related_name="quantity_unit")
    price = models.IntegerField()
    category = models.ForeignKey(GroceryCategory, on_delete=models.SET_NULL,null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Gallery(models.Model):
    items = models.ForeignKey(Grocery, on_delete=models.CASCADE)
    image = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.items.name






from django.db import models

from accounts.models import User
from system.models import ConfigChoice


# Create your models here.
class Grocery(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cover_image = models.ImageField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(ConfigChoice, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Gallery(models.Model):
    items = models.ForeignKey(Grocery, on_delete=models.CASCADE)
    image = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.items.name






from django.db import models

from accounts.models import User
from system.models import ConfigChoice


# Create your models here.
class State(models.Model):
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.street


class Amenities(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='amenities/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    rule = models.TextField()
    category = models.ForeignKey(ConfigChoice, on_delete=models.PROTECT, related_name="room_type")
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    furnishing = models.ForeignKey(ConfigChoice, on_delete=models.PROTECT)
    price = models.FloatField()
    added_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    rating = models.IntegerField()
    review = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.review


class Gallery(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='gallery/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image




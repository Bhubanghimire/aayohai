from django.db import models

from system.models import SoftDeletable


# Create your models here.
class EventCategory(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Event(SoftDeletable):
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    cover_image = models.ImageField(upload_to="events/covers/")
    description = models.TextField()
    event_date = models.DateTimeField()
    start_date = models.DateField()
    # end_date = models.DateTimeField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class FeatureEvent(SoftDeletable):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.event.title


class EventPrice(SoftDeletable):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    available_ticket = models.IntegerField(default=100000)
    limit = models.IntegerField(default=10)
    price = models.IntegerField()  # db will store in cent

    def __str__(self):
        return self.title


class TermsConditions(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

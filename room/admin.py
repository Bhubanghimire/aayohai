from django.contrib import admin
from room.models import Room, Review, Gallery, Amenities, Location, State


# Register your models here.
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'location', 'created_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'rating', 'created_at')


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'room',  'created_at')


@admin.register(Amenities)
class AmenitiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'created_at')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
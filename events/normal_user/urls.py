from django.urls import path, include
from rest_framework.routers import DefaultRouter

from events.normal_user.views import EventModelViewSet, FeaturedEventModelViewSet


event_router = DefaultRouter()
event_router.register(r'event', EventModelViewSet, basename="event")
event_router.register(r'featured', FeaturedEventModelViewSet, basename='featured-event')
# room_router.register(r'room-search', RoomSearchViewSet, basename='room_search')
# room_router.register(r'amenities', AmenitiesViewSet, basename='amenities')
# room_router.register(r"stripe-session", StripeSession, basename="stripe-session")
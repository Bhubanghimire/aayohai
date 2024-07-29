from django.urls import path, include
from rest_framework.routers import DefaultRouter

from system.views import GenderViewSet, RoomViewSet, FurnishingViewSet

choice_router = DefaultRouter()
choice_router.register(r'gender', GenderViewSet, basename="gender")
choice_router.register(r'room', RoomViewSet, basename="room_type")
choice_router.register(r'furnishing', FurnishingViewSet, basename="furnishing")

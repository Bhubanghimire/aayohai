from django.urls import path, include
from rest_framework.routers import DefaultRouter
from room.normal_user.views import DashboardViewSet, RoomViewSet, RoomSearchViewSet

room_router = DefaultRouter()
room_router.register(r'dashboard', DashboardViewSet, basename="dashboard")
room_router.register(r'room', RoomViewSet, basename='room')
room_router.register(r'room-search', RoomSearchViewSet, basename='room_search')


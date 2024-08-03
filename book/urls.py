from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet

book_router = DefaultRouter()
# room_router.register(r'auth', AuthViewSet, basename='auth')

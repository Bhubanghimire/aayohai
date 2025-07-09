from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet, MainViewSet, ProfileViewSet, ChatViewSet

account_router = DefaultRouter()
account_router.register(r'auth', AuthViewSet, basename='auth')
account_router.register(r'main_dashboard', MainViewSet, basename='main_dashboard')
account_router.register(r'profile', ProfileViewSet, basename='profile')
account_router.register(r'chat', ChatViewSet, basename='chat')


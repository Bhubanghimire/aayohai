from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet, MainViewSet

account_router = DefaultRouter()
account_router.register(r'auth', AuthViewSet, basename='auth')
account_router.register(r'main_dashboard', MainViewSet, basename='main_dashboard')


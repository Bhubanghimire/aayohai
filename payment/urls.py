from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet

payment_router = DefaultRouter()

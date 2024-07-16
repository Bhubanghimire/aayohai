from django.urls import path, include
from rest_framework.routers import DefaultRouter

from system.views import GenderViewSet

choice_router = DefaultRouter()
choice_router.register(r'gender', GenderViewSet)

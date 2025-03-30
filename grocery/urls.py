from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet

grocery_router = DefaultRouter()
grocery_router.register(r'list', AuthViewSet,basename="grocery_list")
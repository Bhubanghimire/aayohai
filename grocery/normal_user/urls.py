from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet
from grocery.normal_user.views import GroceryDashboardViewSet, RoomSearchViewSet

grocery_router = DefaultRouter()
grocery_router.register(r'dashboard', GroceryDashboardViewSet, basename="grocery_dashboard")
grocery_router.register(r'search-list', RoomSearchViewSet, basename="grocery_search")

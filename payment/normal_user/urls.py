from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet
from payment.normal_user.views import TicketViewSet

payment_router = DefaultRouter()
payment_router.register(r'ticket', TicketViewSet, basename="dashboard")
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet
from book.normal_user.views import CartViewSet, StripeSession


book_router = DefaultRouter()
book_router.register(r'cart', CartViewSet, basename="cart")
book_router.register("payment_intent", StripeSession, basename="payment-intent")

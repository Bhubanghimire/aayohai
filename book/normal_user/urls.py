from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet
from book.normal_user.views import CartViewSet, StripeSession, BookEventList, GroceryBookList, RoomBookList

book_router = DefaultRouter()
book_router.register(r'cart', CartViewSet, basename="cart")
book_router.register("payment_intent", StripeSession, basename="payment-intent")
book_router.register('grocery-book-list', GroceryBookList, basename="grocery-event-list")
book_router.register('room-book-list', RoomBookList, basename="room-book-list")
book_router.register('event-book-list', BookEventList, basename="event-book-list")

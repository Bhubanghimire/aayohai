from rest_framework.decorators import action
from accounts.models import Advertise
from accounts.serializers import AdvertiseSerializer
from book.models import Cart, Book, BookItem, EventItem, OrderItem
from book.serializers import GartSerializers
from django.db import transaction
from events.models import Event, EventPrice
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

from payment.models import Invoice
from system.models import ConfigChoice
from system.serializers import ConfigChoiceSerializer
import json
import stripe
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.urls.base import reverse

from django.utils.html import strip_tags
from rest_framework.response import Response
import jwt
from rest_framework.response import Response
from rest_framework import serializers, viewsets, status

from django.contrib.auth import authenticate
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST
)
from rest_framework import exceptions
#
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import action
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from tutorial.quickstart.serializers import UserSerializer

from aayohai.settings import HOST_URL
from room.models import Room, State, Location, Gallery, Amenities
from room.serializers import RoomSerializers, StateSerializer, RoomDetailSerializer, RoomSearchSerializer, \
    RoomCreateSerializer, AmenitiesSerializer
from system.serializers import ConfigChoiceSerializer
from accounts.models import User


# Create your views here.


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = GartSerializers


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeSession(viewsets.ModelViewSet):
    queryset = Amenities.objects.all()
    serializer_class = AmenitiesSerializer

    @transaction.atomic
    def create(self, request):
        data = request.data
        currency = data.get('currency', 'aud')
        ids = data.get('object_ids', [])
        table_object = data.get('object')

        book_obj = Book.objects.create(user=request.user, status_id=1)

        total_amount = 0
        if table_object == "Room":
            for room_id in ids:
                room_obj = Room.objects.get(pk=room_id)
                total_amount += room_obj.price
                BookItem.objects.create(book=book_obj, room=room_obj, price=room_obj.price,
                                        total_amount=room_obj.price)

        elif table_object == "Event":
            for event in ids:
                event_price = EventPrice.objects.get(id=event['price_id'])
                total_amount += event_price.price*event['count']
                EventItem.objects.create(book=book_obj, event_id=event['event_id'], price=event_price.price,
                                         count=event['count'],
                                         total_amount=event_price.price*event['count'])
        elif table_object == "Grocery":
            for grocery in ids:
                total_amount += grocery["price"]
                OrderItem.objects.create(book=book_obj, grocery_id=grocery['id'], price=grocery["price"],
                                         total_amount=grocery["price"])

        last_inovice = Invoice.objects.last()
        if last_inovice:
            invoice_number = last_inovice.invoice_number + 1
        else:
            invoice_number = 1000
        Invoice.objects.create(book=book_obj, invoice_amount=total_amount, invoice_number=invoice_number,
                               total_amount=total_amount)

        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),
            currency=currency,
            metadata={'integration_check': 'accept_a_payment'},
        )
        return Response({
            'clientSecret': intent.client_secret,
            "book_id": book_obj.uuid,
        })



    @action(detail=False, methods=['post'])
    def update_status(self, request):
            data = request.data
            book = data.get('book')
            payment_complete = data.get('payment_complete')
            reference_id = data.get('reference_id')
            Invoice.objects.filter(book=book).update(payment_complete=payment_complete, reference_id=reference_id)
            return Response({
                'message': "Updated payment complete",
            })



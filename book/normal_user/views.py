from django.db.models.aggregates import Sum
from rest_framework.decorators import action
from accounts.models import Advertise
from accounts.pagination import CustomPagination
from accounts.serializers import AdvertiseSerializer
from book.middleware import createUnique, CreateTicketFunction, send_mail_with_ticket
from book.models import Cart, Book, BookItem, EventItem, OrderItem
from book.serializers import GartSerializers, BookEventSerializer, OrderItemSerializer, BookItemSerializer
from django.db import transaction
from events.models import Event, EventPrice
from events.serializers import EventSerializers
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

from payment.models import Invoice, Ticket
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Cart list fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        check_exists = Cart.objects.filter(user=request.user, grocery_id=data['grocery'])
        if check_exists.exists():
            check_exists.update(quantity=data['quantity'])
            return Response({
                'message': 'Item updated to cart successfully.',
            }, status=200)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'message': 'Item added to cart successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'message': 'Cart item updated successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'Cart item deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeSession(viewsets.ModelViewSet):
    queryset = Amenities.objects.all()
    serializer_class = AmenitiesSerializer
    permission_classes = [IsAuthenticated]

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
                room_obj = Room.objects.filter(pk=room_id).first()
                total_amount += room_obj.price
                BookItem.objects.create(book=book_obj, room=room_obj, price=room_obj.price,
                                        total_amount=room_obj.price)

        elif table_object == "Event":
            for event in ids:
                event_price = EventPrice.objects.get(id=event['price_id'])
                total_amount += event_price.price * event['count']
                EventItem.objects.create(book=book_obj, event_id=event['event_id'], price=event_price.price,
                                         count=event['count'],
                                         total_amount=event_price.price * event['count'])
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
        Invoice.objects.filter(book=book).update(payment_status=payment_complete, reference_id=reference_id)
        event_items = EventItem.objects.filter(book=book)
        if event_items.exists():
            event = event_items.first().event
            for event_rate in event_items:
                price = event_rate.event_price
                total_count = price.available_ticket
                ticket_count = Ticket.objects.filter(event=event, event_price=price).aggregate(Sum("no_of_ticket"))[
                    'no_of_ticket__sum']
                if not ticket_count:
                    ticket_count = 0

                if (total_count - ticket_count) < event_rate.count:
                    return JsonResponse({"message": "No ticket available."})

                ticket_obj = Ticket.objects.create(
                    user=self.request.user,
                    event=event,
                    event_price=price,
                    invoice=Invoice.objects.filter(book=book).first(),
                    ticket_number=createUnique(),
                    ticket_bought=True,
                    scanned=False,
                    no_of_ticket=event_rate.count
                )
                #
                img, qr = CreateTicketFunction(request, ticket_obj, event.title)
                Ticket.objects.filter(id=ticket_obj.id).update(ticket_img=img, qr_img=qr)
                try:
                    send_mail_with_ticket((ticket_obj))
                except Exception:
                    print("mail send error")
                    pass

        return Response({
            'message': "Updated payment complete",
        })


class BookEventList(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookEventSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        final_query = queryset.filter(eventitem__isnull=False).distinct()
        return final_query

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        final_list = []
        for obj in queryset:
            event_item = EventItem.objects.filter(book=obj).first()
            json_obj = {
                "uuid": obj.uuid,
                "event": EventSerializers(event_item.event).data,
                "status": obj.status.name,
                "event_price": {"id": event_item.event_price.id,
                                "title": event_item.event_price.title,
                                "price": event_item.event_price.price},
                "count": event_item.count,
                "total_amount": event_item.total_amount
            }
            final_list.append(json_obj)

        return JsonResponse({"data": final_list})


class GroceryBookList(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookEventSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user)
        queryset = super().get_queryset().filter(user=self.request.user)
        final_query = queryset.filter(orderitem__isnull=False).distinct()
        return final_query

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        final_list = []
        for obj in queryset:
            event_item = OrderItem.objects.filter(book=obj)
            json_obj = {
                "uuid": obj.uuid,
                "grocery": OrderItemSerializer(event_item, many=True).data,
                "status": obj.status.name,
            }
            final_list.append(json_obj)

        return JsonResponse({"data": final_list})


class RoomBookList(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookEventSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        final_query = queryset.filter(bookitem__isnull=False).distinct()
        return final_query

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        final_list = []
        for obj in queryset:
            book_item = BookItem.objects.filter(book=obj)
            json_obj = {
                "uuid": obj.uuid,
                "room": BookItemSerializer(book_item, many=True).data,
                "status": obj.status.name,
            }
            final_list.append(json_obj)

        return JsonResponse({"data": final_list})

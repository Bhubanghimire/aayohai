from rest_framework.decorators import action
from accounts.models import Advertise
from accounts.serializers import AdvertiseSerializer
from book.models import Cart
from book.serializers import GartSerializers
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

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

    def create(self, request):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": 500,  # Amount in cents (e.g., $10.00)
                            "product_data": {
                                "name": "Sample Product",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{HOST_URL}/api/room/stripe-session/stripe_webhook/",
                # cancel_url="/api/room/dashboard/",
            )
            return Response({"checkout_url": checkout_session.url}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error vo", e)
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def stripe_webhook(self, request):
        payload = request.body  # ✅ Ensure raw body is used
        sig_header = request.headers.get("Stripe-Signature")

        if not sig_header:
            return JsonResponse({"error": "Missing Stripe-Signature header"}, status=400)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe.api_key
            )

            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                print("Payment Successful:", session)

        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({"error": f"Signature verification failed: {str(e)}"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": f"Invalid payload: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        return JsonResponse({"message": "Webhook received"}, status=200)

    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        try:
            data = request.data
            amount = int(data.get('amount', 200))  # in paisa/cents
            currency = data.get('currency', 'usd')

            # Optional: add customer metadata, description
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={'integration_check': 'accept_a_payment'},
            )

            return Response({
                'clientSecret': intent.client_secret
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

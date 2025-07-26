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
from room.models import Room, State, Location, Gallery, Amenities, Review
from room.serializers import RoomSerializers, StateSerializer, RoomDetailSerializer, RoomSearchSerializer, \
    RoomCreateSerializer, AmenitiesSerializer, ReviewSerializer
from system.serializers import ConfigChoiceSerializer
from accounts.models import User


# Create your views here.


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializers
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super().get_queryset().exclude(status_id=18)  # Exclude rooms with status 'Sold'
        return queryset

    @action(methods=['get'], detail=False, url_path='nearby')
    def nearby(self, request, user_id=None):
        # category = self.request.query_params.get('category', None)
        # latitude = self.request.query_params.get('latitude', None)
        # longitude = self.request.query_params.get('longitude', None)

        #TODO: implement filter
        rooms = self.get_queryset()
        serializer_data = self.serializer_class(rooms, many=True).data

        return JsonResponse({'data': serializer_data, 'message': 'nearby room list.'})

    @action(methods=['get'], detail=False, url_path='cities')
    def cities(self, request, user_id=None):
        cities = State.objects.all()
        state_serializer = StateSerializer(cities, many=True).data
        return JsonResponse({'data': state_serializer, 'message': 'state list data.'})


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer

    # permission_classes = [AllowAny]

    def get_queryset(self):
        added_by_me = self.request.query_params.get("added_by_me", False)
        if added_by_me:
            return super().get_queryset().filter(added_by=self.request.user.id)
        queryset = super().get_queryset().exclude(status_id=18)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        request.data._mutable = True
        images = request.FILES.getlist('image')

        # Parse 'amenities' from JSON string if needed
        if isinstance(data.get('amenities'), str):
            data['amenities'] = json.loads(data['amenities'])

        # Add other necessary fields
        location_data = json.loads(data.get('location'))
        print(location_data)
        state = State.objects.get_or_create(country=location_data['country'], name=location_data['state'])[0]
        location_data.pop('state')
        location_data.pop('country')
        location = Location.objects.create(state=state, **location_data)
        data['location'] = location.pk
        data['added_by'] = request.user.id
        data['status'] = 16  # Assuming '1' is the default status ID
        request.data._mutable = False

        serializer = RoomCreateSerializer(data=data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    instance = serializer.save()

                    # Add amenities after instance is created
                    for amenity_id in data['amenities']:
                        instance.amenities.add(amenity_id)

                    instance.save()
                    for image in images:
                        Gallery.objects.create(room=instance, image=image)
                return JsonResponse({"data": serializer.data, "message": "room added successfully."}, status=201)
            except Exception as e:
                print("Error while saving room:", str(e))
                return JsonResponse({"error": str(e)}, status=400)
        else:
            print("error vo", serializer.errors)
            return JsonResponse(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        room = self.get_object()

        serializer = self.serializer_class(room)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        request.data._mutable = True
        images = request.FILES.getlist('image')

        # Parse amenities if passed as JSON string
        if isinstance(data.get('amenities'), str):
            data['amenities'] = json.loads(data['amenities'])
            instance.amenities.clear()

        # Handle location update
        if data.get('location'):
            location_data = json.loads(data.get('location'))
            state = State.objects.get_or_create(
                country=location_data['country'],
                name=location_data['state']
            )[0]
            location_data.pop('state')
            location_data.pop('country')

            # Update the existing Location or create new one
            if instance.location:
                for key, value in location_data.items():
                    setattr(instance.location, key, value)
                instance.location.state = state
                instance.location.save()
                location_id = instance.location.id
            else:
                location = Location.objects.create(state=state, **location_data)
                location_id = location.id

            data['location'] = location_id

        # Ensure added_by remains same or assign if missing
        data['added_by'] = getattr(instance, 'added_by_id', request.user.id)

        # Status fallback if not provided
        # if not data.get('status'):
        #     data['status'] = 16

        request.data._mutable = False

        serializer = RoomCreateSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    room = serializer.save()

                    # Update amenities
                    if 'amenities' in data:
                        room.amenities.set(data['amenities'])

                    # Add new images if provided
                    for image in images:
                        Gallery.objects.create(room=room, image=image)

                return JsonResponse(
                    {"data": RoomDetailSerializer(room).data, "message": "Room updated successfully."},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                print("Error while updating room:", str(e))
                return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Validation errors:", serializer.errors)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='status-update')
    def status_update(self, request, pk=None):
        room = self.get_object()
        status_id = request.data.get('status_id')
        room.status_id = status_id
        room.save()

        return Response({"message": "Status updated successfully."}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='review')
    def review(self, request, pk=None):
        room = Room.objects.get(id=pk)
        user = request.user
        post_data = request.data
        post_data['user'] = user.id

        # Check if the user has already reviewed this room
        try:
            review_instance = Review.objects.get(room=room, user=user)
            # Update existing review
            serializer = ReviewSerializer(review_instance, data=request.data, context={'request': request})
        except Review.DoesNotExist:
            # Create a new review
            serializer = ReviewSerializer(data=post_data, context={'request': request})

        if serializer.is_valid():
            serializer.save(user=user, room=room)
            response = {
                "message": "Review submitted successfully.",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='image-delete')
    def image_delete(self, request, pk=None):
        room = self.get_object()
        image_id = request.data.get('image_id')
        user = request.user

        try:
            image = Gallery.objects.get(room=room,room__added_by=user, id=image_id)
            image.delete()
            return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
        except Gallery.DoesNotExist:
            return Response({"message": "Image not found."}, status=status.HTTP_404_NOT_FOUND)


class RoomSearchViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSearchSerializer

    # permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset().exclude(status_id=18)  # Exclude rooms with status 'Sold'
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)
        furnishing = self.request.query_params.get('furnishing', None)
        location = self.request.query_params.get('location', None)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if category:
            queryset = queryset.filter(category=category)

        if furnishing:
            queryset = queryset.filter(furnishing=furnishing)

        if location:
            loc = Location.objects.filter(state_id=location)
            queryset = queryset.filter(location__in=loc)

        return queryset

    # def retrieve(self, request, pk=None):
    #     room = self.get_object()
    #     serializer = self.serializer_class(room)
    #     return Response(serializer.data)


class AmenitiesViewSet(viewsets.ModelViewSet):
    queryset = Amenities.objects.all()
    serializer_class = AmenitiesSerializer


stripe.api_key = "sk_test_51PlsK0LZ4Y3l2niTCIL3G1YiWCv7V1hNcHH7LWPehTgOy53ZYaT5oBtKiSJoAAxokvBB1JBil5cxEiFVFFIaQX9P000DqfINHa"


class StripeSession(viewsets.ModelViewSet):
    queryset = Amenities.objects.all()
    serializer_class = AmenitiesSerializer
    permission_classes = [IsAuthenticated]

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

    @action(detail=False, methods=['post'])  # ✅ Change 'get' → 'post'
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

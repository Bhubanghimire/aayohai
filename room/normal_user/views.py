import json

from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction

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
from room.models import Room, State, Location, Gallery, Amenities
from room.serializers import RoomSerializers, StateSerializer, RoomDetailSerializer, RoomSearchSerializer, \
    RoomCreateSerializer, AmenitiesSerializer
from system.serializers import ConfigChoiceSerializer
from accounts.models import User
# Create your views here.



class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializers
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super().get_queryset()
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
        queryset = super().get_queryset()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        images = request.FILES.getlist('image')

        # Parse 'amenities' from JSON string if needed
        if isinstance(data.get('amenities'), str):
            data['amenities'] = json.loads(data['amenities'])


        # Add other necessary fields
        location_data = json.loads(data.get('location'))
        state = State.objects.get_or_create(country=location_data['country'], name=location_data['state'])[0]
        location_data.pop('state')
        location_data.pop('country')
        location = Location.objects.create(state=state, **location_data)
        data['location'] = location.pk
        data['added_by'] = request.user.id

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
            return JsonResponse(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        room = self.get_object()

        serializer = self.serializer_class(room)
        return Response(serializer.data)


class RoomSearchViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSearchSerializer
    # permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
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

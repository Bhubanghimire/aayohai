from django.http import JsonResponse
from django.shortcuts import render

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
from room.models import Room, State
from room.serializers import RoomSerializers, StateSerializer, RoomDetailSerializer
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

    def retrieve(self, request, pk=None):
        print("test", pk)
        room = self.get_object()

        serializer = self.serializer_class(room)
        return Response(serializer.data)

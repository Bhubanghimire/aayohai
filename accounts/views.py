import json
import os
from datetime import datetime, timedelta

from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.views.generic.base import TemplateView
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
from accounts.middleware import generate_access_token, generate_refresh_token, generate_otp
from accounts.models import OTP, Advertise
from accounts.serializers import UserSerializers, AdvertiseSerializer, UserUpdateSerializer
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from room.models import Room
from room.serializers import RoomSerializers

# from accounts.models import OTP
# from .serializers import UserSerializers
#
User = get_user_model()

class Homepage(TemplateView):
    template_name = "homepage.html"

class AuthViewSet(viewsets.ViewSet):
    permission_classes_by_action = {
        'refresh': [IsAuthenticated],
        'login': [AllowAny],
        'signup_otp': [AllowAny],
        'register': [AllowAny],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['POST'], url_path='refresh')
    def refresh(self, request):
        token = request.POST.get('refresh_token')
        if token is None:
            return Response({"message": "please send refresh token in payload"}, status=HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Refresh Token expired')
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid Refresh Token")

        user = User.objects.filter(id=payload.get('user_id')).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        response = {
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            "message": "New Generated Credentials."
        }
        return Response(response)

    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request):
        password = request.data.get('password', False)
        email = request.data.get('email', False)

        if not (email or password):
            raise serializers.ValidationError(
                {"message": "Enter Email and password"}
            )

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is None:
            raise serializers.ValidationError(
                {"message": "A user with this email and password was not found."}
            )

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response = {
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            "message": "loggedIn successfully."
        }
        return Response(response, status=HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='send-otp')
    def otp_send(self, request):
        data = request.data
        email = data['email']
        generated_otp = generate_otp()
        check_status = OTP.objects.filter(email=email)
        print("status", check_status)
        if check_status.exists():
            check_status.update(otp=generated_otp)
            print("updated", check_status)
        else:
            obj = OTP.objects.create(email=email, otp=generated_otp)
            print("obj created", obj)
        context = {'title': 'Otp', 'content': generated_otp}
        html_content = render_to_string("email_template.html", context=context)
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Otp for email verification', text_content, settings.DEFAULT_FROM_EMAIL, [email])
        email.attach_alternative(html_content, 'text/html')
        try:
            email.send()
        except Exception as e:
            print(e)
            return Response({"message": "Email not sending. Try again."}, status=HTTP_400_BAD_REQUEST)

        return Response({'message': 'OTP is sent to provided email.'})

    @action(detail=False, methods=['POST'], url_path='register')
    def register(self, request):
        data = request.data
        try:
            check_otp = OTP.objects.get(email=data['email'], otp=data['otp'])
        except OTP.DoesNotExist:
            return Response({'message': 'OTP not found'}, status=HTTP_400_BAD_REQUEST)

        # if User.objects.filter(email=data['email']).exists():
        #     return Response({'message': 'User already exists'}, status=HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializers(data=data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        check_otp.delete()
        user = User.objects.get(id=user_serializer.data["id"])
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response = {
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            "message": "loggedIn successfully."
        }
        return Response(response, status=HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='forget-password')
    def forget_password(self, request):
        data = request.data
        check_otp = OTP.objects.filter(email=data['email'], otp=data['otp'])
        if check_otp.exists():
            try:
                user = User.objects.get(email=data['email'])
            except Exception:
                return Response({'message': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(data['new_password'])
            user.save()
            return Response({'message': 'Done'})
        else:
            return Response({'message': 'Otp is not matched'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path='otp-verify')
    def otp_verify(self, request):
        data = request.data
        check_otp = OTP.objects.filter(email=data['email'], otp=data['otp'])
        if check_otp.exists():
            return JsonResponse({'message': 'OTP  matched'}, status=status.HTTP_200_OK)
        return Response({'message': 'OTP not matched'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path='password-change')
    def change_password(self, request, *args, **kwargs):
        user = self.request.user
        old_pw = request.data.get('old_password', False)
        new_pw = request.data.get('new_password')

        if (old_pw or new_pw) is None:
            return Response({'data': {}, 'message': 'Please provide old and new password!'}, status=400)

        if check_password(old_pw, user.password):
            user.set_password(new_pw)
            user.save()
            return Response({'data': {}, 'message': 'Password changed successfully!'}, status=200)
        else:
            return Response({'data': {}, 'message': 'The Old Password does not match!'}, status=400)


class MainViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['GET'], url_path='advertise')
    def advertise(self, request):
        ad_list = Advertise.objects.filter(active=True)
        serializer = AdvertiseSerializer(ad_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    @action(detail=False, methods=['GET'], url_path='new-arrival')
    def new_arrival(self, request):
        # seven_days_ago = datetime.now() - timedelta(days=7)
        ad_list = Room.objects.all().order_by("-id")[0:5]    #filter(created_at__gte=seven_days_ago)
        serializer = RoomSerializers(ad_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    @action(detail=False, methods=['GET'], url_path='groceries')
    def groceries(self, request):
        seven_days_ago = datetime.now() - timedelta(days=7)
        grocery_list = Grocery.objects.all().order_by("-id")[0:5]   #filter(created_at__gte=seven_days_ago)
        serializer = GrocerySerializers(grocery_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = self.request.user
        serializer = UserSerializers(user).data
        serializer.pop('password')
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    def put(self, request):
        user = self.request.user
        profile = request.FILES.get('profile')
        if profile:
            if user.profile:
                os.remove(user.profile.path)
            user.profile = profile
            user.save()

        required_fields = ['first_name', 'last_name', 'birth_date', 'gender']
        missing_fields = [field for field in required_fields if
                          field not in request.data or request.data[field] in [None, '']]

        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()


            return Response({'data': serializer.data, 'message': 'Data updated.'})
        else:
            return Response({'data': serializer.errors, 'message': 'Data update failed.'})

    @action(detail=False, methods=['delete'])
    def delete_user(self, request):
        data = json.loads(request.body)
        user_obj = User.objects.filter(id=data['user_id'])
        otp = data['otp']

        if user_obj.exists():
            user = user_obj.first()
            otp_check = OTP.objects.filter(email=user.email, otp=otp)
            if not otp_check.exists():
                return Response({'message': 'OTP not found'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_deleted = True
            user.deleted_at = datetime.now()
            user.save()
            otp_check.delete()
            # user.delete()
            return Response({'message': 'User deleted.'}, status=200)
        else:
            return Response({'message': 'User does not exist.'}, status=404)

    # def retrieve(self, request, pk=None):
    #     # Not using pk, returning the authenticated user

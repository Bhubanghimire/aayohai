from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
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
from accounts.middleware import generate_access_token, generate_refresh_token, generate_otp
from accounts.models import OTP, Advertise
from accounts.serializers import UserSerializers, AdvertiseSerializer
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from room.models import Room
from room.serializers import RoomSerializers

# from accounts.models import OTP
# from .serializers import UserSerializers
#
User = get_user_model()


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

        if check_status.exists():
            check_status.update(otp=generated_otp)
        else:
            OTP.objects.create(email=email, otp=generated_otp)

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


class MainViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['GET'], url_path='advertise')
    def advertise(self, request):
        ad_list = Advertise.objects.filter(active=True)
        serializer = AdvertiseSerializer(ad_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    @action(detail=False, methods=['GET'], url_path='new-arrival')
    def new_arrival(self, request):
        seven_days_ago = datetime.now() - timedelta(days=7)
        ad_list = Room.objects.filter(created_at__gte=seven_days_ago)
        serializer = RoomSerializers(ad_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    @action(detail=False, methods=['GET'], url_path='groceries')
    def groceries(self, request):
        seven_days_ago = datetime.now() - timedelta(days=7)
        grocery_list = Grocery.objects.filter(created_at__gte=seven_days_ago)
        serializer = GrocerySerializers(grocery_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})


class ProfileViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        user = User.objects.filter().first()  # request.user
        serializer = UserSerializers(user).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    # def retrieve(self, request, pk=None):
    #     # Not using pk, returning the authenticated user

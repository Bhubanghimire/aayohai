from rest_framework import serializers
from django.contrib.auth import get_user_model
User=get_user_model()


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "birth_date", "gender"]


class UserDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", 'profile']

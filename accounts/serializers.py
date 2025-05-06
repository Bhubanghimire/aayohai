from rest_framework import serializers
from django.contrib.auth import get_user_model

from accounts.models import Advertise

User = get_user_model()


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", 'profile', "birth_date", "gender"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['gender'] = instance.gender.name if instance.gender else "Male"
        return rep
        # self.fields['gender'] = str(instance.gender.name)
        # return super(UserSerializers, self).to_representation(instance)


class UserDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", 'profile']


class AdvertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertise
        fields = ['id', "ad"]

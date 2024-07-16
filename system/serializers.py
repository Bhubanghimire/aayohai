from rest_framework import serializers
from .models import ConfigChoice


class ConfigChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigChoice
        fields = ['id', 'name', 'image', 'description']



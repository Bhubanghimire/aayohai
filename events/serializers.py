from events.models import Event, EventCategory, EventPrice
from rest_framework import serializers


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ("title",)


class EventPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPrice
        fields = ("id", "price", "title", "available_ticket", "limit")


class EventSerializers(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', "title", "category", "cover_image", "description", "event_date", "location"]
        # exclude = ("start_date", "end_date")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = EventCategorySerializer(instance.category).data
        price = EventPrice.objects.filter(event=instance)
        rep['price'] = EventPriceSerializer(price, many=True).data
        return rep


class TermsConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title']

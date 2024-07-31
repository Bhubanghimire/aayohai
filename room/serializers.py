from django.db.models import Sum
from rest_framework import serializers
from room.models import Room, Location, State, Review, Gallery
from system.serializers import ConfigChoiceSerializer
from accounts.serializers import UserSerializers


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['image']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['state'] = StateSerializer(read_only=True)
        return super(LocationSerializer, self).to_representation(instance)


class RoomSerializers(serializers.ModelSerializer):
    review = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id",
                  "name",
                  "price",
                  "category",
                  "location",
                  "review",
                  "cover_image"
                  ]

    def get_review(self, obj):
        review = Review.objects.filter(room=obj).aggregate(Sum('rating'))['rating__sum']
        if review is None:
            review = 0.0
        return review

    def get_cover_image(self, obj):
        print(obj)
        cover_image = Gallery.objects.filter(room=obj).first()
        print(cover_image)
        cover_image = GallerySerializer(cover_image).data
        return cover_image["image"]

    def to_representation(self, instance):
        self.fields['location'] = LocationSerializer(read_only=True)
        self.fields['category'] = ConfigChoiceSerializer(read_only=True)
        # self.fields['review'] = UserSerializers(read_only=True)
        return super(RoomSerializers, self).to_representation(instance)

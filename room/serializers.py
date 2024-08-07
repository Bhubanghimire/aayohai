from django.db.models import Sum
from rest_framework import serializers
from room.models import Room, Location, State, Review, Gallery, Amenities
from system.serializers import ConfigChoiceSerializer
from accounts.serializers import UserDetailSerializers


class AmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenities
        fields = '__all__'


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['image']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "rating", "review", "user"]

    def to_representation(self, instance):
        self.fields['user'] = UserDetailSerializers(read_only=True)
        return super(ReviewSerializer, self).to_representation(instance)


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
        cover_image = Gallery.objects.filter(room=obj).first()
        cover_image = GallerySerializer(cover_image).data
        return cover_image["image"]

    def to_representation(self, instance):
        self.fields['location'] = LocationSerializer(read_only=True)
        self.fields['category'] = ConfigChoiceSerializer(read_only=True)
        # self.fields['review'] = UserSerializers(read_only=True)
        return super(RoomSerializers, self).to_representation(instance)


class RoomDetailSerializer(RoomSerializers):
    reviews = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'amenities', 'rule', 'length', 'breadth', 'price', 'review', 'reviews', 'gallery']

    def to_representation(self, instance):
        self.fields['state'] = StateSerializer(read_only=True)
        self.fields['amenities'] = AmenitiesSerializer(many=True, read_only=True)
        return super(RoomDetailSerializer, self).to_representation(instance)

    def get_gallery(self, obj):
        gallery = Gallery.objects.filter(room=obj)
        gallery = GallerySerializer(gallery, many=True).data
        return gallery

    def get_reviews(self, obj):
        reviews = Review.objects.filter(room=obj)
        reviews_serializers = ReviewSerializer(reviews, many=True).data
        return reviews_serializers


class RoomSearchSerializer(RoomSerializers):
    class Meta:
        model = Room
        fields = ['id', 'name', 'category', 'price', "cover_image"]


class RoomCreateSerializer(serializers.ModelSerializer):
    # amenities = serializers.PrimaryKeyRelatedField(many=True, queryset=Amenities.objects.all())

    class Meta:
        model = Room
        # fields = '__all__'
        exclude = ['amenities']
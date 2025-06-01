from rest_framework import serializers
from book.models import Cart, Book, OrderItem, BookItem, EventItem
from events.serializers import EventSerializers
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from room.serializers import RoomSearchSerializer


class GartSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'grocery', 'quantity']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['grocery'] = GrocerySerializers(instance.grocery).data
        return rep


class BookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ('is_deleted', 'deleted_at', 'created_at', 'updated_at')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"
        # exclude = ('is_deleted', 'deleted_at', 'created_at', 'updated_at')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['grocery'] = GrocerySerializers(instance.grocery).data
        return rep


class BookItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookItem
        exclude = ('is_deleted', 'deleted_at', 'created_at', 'updated_at')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['room'] = RoomSearchSerializer(instance.room).data
        return rep


class EventItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventItem
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['event'] = EventSerializers(instance.event).data
        return rep
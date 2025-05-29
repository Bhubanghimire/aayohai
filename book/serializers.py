from rest_framework import serializers
from book.models import Cart, Book, OrderItem, BookItem
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
        exclude = ('is_deleted', 'deleted_at', 'created_at', 'updated_at')

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

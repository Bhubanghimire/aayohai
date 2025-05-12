from rest_framework import serializers
from book.models import Cart, Book
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers


class GartSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['grocery'] = GrocerySerializers(instance.grocery).data
        return rep


class BookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ('is_deleted', 'deleted_at')


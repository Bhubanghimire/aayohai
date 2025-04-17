from rest_framework import serializers
from grocery.models import Grocery


class GrocerySerializers(serializers.ModelSerializer):
    class Meta:
        model = Grocery
        fields = ["id", "name", "description", "cover_image", "price", "quantity", "quantity_unit", "category"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['quantity_unit'] = str(instance.quantity_unit.name)
        # self.fields['review'] = UserSerializers(read_only=True)
        return rep
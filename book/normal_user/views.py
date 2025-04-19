from rest_framework.decorators import action
from accounts.models import Advertise
from accounts.serializers import AdvertiseSerializer
from book.models import Cart
from book.serializers import GartSerializers
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

from system.models import ConfigChoice
from system.serializers import ConfigChoiceSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = GartSerializers

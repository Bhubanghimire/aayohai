from rest_framework.decorators import action
from accounts.models import Advertise
from accounts.serializers import AdvertiseSerializer
from grocery.models import Grocery
from grocery.serializers import GrocerySerializers
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

from system.models import ConfigChoice
from system.serializers import ConfigChoiceSerializer


class GroceryDashboardViewSet(viewsets.ModelViewSet):
    queryset = Grocery.objects.all()
    serializer_class = GrocerySerializers
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    @action(detail=False, methods=['GET'], url_path='advertise')
    def advertise(self, request):
        ad_list = Advertise.objects.filter(active=True)
        serializer = AdvertiseSerializer(ad_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})

    @action(detail=False, methods=['GET'], url_path='category-list')
    def category(self, request):
        ad_list = ConfigChoice.objects.filter(status=True, category__name='grocery_category')
        serializer = ConfigChoiceSerializer(ad_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})


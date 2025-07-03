from rest_framework.decorators import action
from accounts.models import Advertise
from accounts.serializers import AdvertiseSerializer
from grocery.models import Grocery, GroceryCategory
from grocery.serializers import GrocerySerializers, GroceryCategorySerializer
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
        cat_list = GroceryCategory.objects.filter(status=True)
        serializer = GroceryCategorySerializer(cat_list, context={"request": request}, many=True).data
        return Response({'data': serializer, 'message': 'Data Fetched.'})


class RoomSearchViewSet(viewsets.ModelViewSet):
    queryset = Grocery.objects.all()
    serializer_class = GrocerySerializers

    # permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)
        # furnishing = self.request.query_params.get('furnishing', None)
        # location = self.request.query_params.get('location', None)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if category:
            queryset = queryset.filter(category=category)

        # if furnishing:
        #     queryset = queryset.filter(furnishing=furnishing)
        #
        # if location:
        #     loc = Location.objects.filter(state_id=location)
        #     queryset = queryset.filter(location__in=loc)

        return queryset
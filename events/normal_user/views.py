from events.models import Event, TermsConditions, FeatureEvent
from rest_framework import serializers, viewsets, status, filters
from events.serializers import EventSerializers, TermsConditionsSerializer
from rest_framework.response import Response
import datetime


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', "location"]

    def get_queryset(self):
        today_date = datetime.date.today()
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)
        status = self.request.query_params.get('status')
        if status == "upcoming":
            queryset = queryset.filter(start_date__gt=today_date)
        else:
            queryset = queryset.filter(start_date__lte=today_date)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method to fetch a single event.
        You can modify the response format or add extra logic here.
        """
        instance = self.get_object()  # Gets the event based on URL pk/id

        # Example: Add additional data to the response
        serializer = self.get_serializer(instance)
        response_data = serializer.data
        terms_and_conditions = TermsConditions.objects.filter(event=instance)
        response_data['terms'] = TermsConditionsSerializer(terms_and_conditions, many=True).data
        return Response(response_data)


class FeaturedEventModelViewSet(viewsets.ModelViewSet):
    queryset = FeatureEvent.objects.all()
    serializer_class = EventSerializers

    def get_queryset(self):
        today_date = datetime.date.today()
        queryset = super().get_queryset().filter(start_date__lte=today_date, end_date__gte=today_date, status=True)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().values_list("event", flat=True)
        events = Event.objects.filter(pk__in=queryset)
        serializer = EventSerializers(events, many=True, context={"request": request})
        return Response(serializer.data)


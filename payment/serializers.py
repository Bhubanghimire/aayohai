from django.db.models import Sum, Avg
from rest_framework import serializers

from events.serializers import EventPriceDetailSerializer, EventSerializers
from payment.models import Ticket, Invoice
from room.models import Room, Location, State, Review, Gallery, Amenities
from system.serializers import ConfigChoiceSerializer
from accounts.serializers import UserDetailSerializers


class InvoiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class TicketSerializers(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = UserDetailSerializers(instance.user).data
        rep['event_price'] = EventPriceDetailSerializer(instance.event_price).data
        rep['event'] = EventSerializers(instance.event).data
        rep['invoice'] = InvoiceSerializers(instance.invoice).data
        return rep
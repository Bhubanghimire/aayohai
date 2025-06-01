from rest_framework import serializers, viewsets, status
from payment.models import Ticket
from payment.serializers import TicketSerializers
from rest_framework.response import Response


# Create your views here.
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializers
    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(event_id=self.kwargs['pk'], user=self.request.user).first()
        serializer = self.get_serializer(instance)

        # Custom logic here, e.g., modify data or add additional fields
        data = serializer.data

        return Response(data)

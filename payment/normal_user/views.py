from rest_framework import serializers, viewsets, status

from book.models import Book, BookItem, OrderItem, EventItem
from book.serializers import BookEventSerializer, OrderItemSerializer, BookItemSerializer, EventItemSerializer
from payment.models import Ticket, Invoice
from payment.serializers import TicketSerializers, InvoiceSerializers
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


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializers
    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(book_id=self.kwargs['pk'],
                                   book__user=self.request.user).first()

        event_obj = Book.objects.filter(uuid=self.kwargs['pk'],
                                              user=self.request.user,
                                              eventitem__isnull=False).first()

        grocery_obj = Book.objects.filter(uuid=self.kwargs['pk'],
                                               user=self.request.user,
                                               orderitem__isnull=False).first()

        room_obj = Book.objects.filter(uuid=self.kwargs['pk'],
                                               user=self.request.user,
                                               bookitem__isnull=False).first()
        serializer = self.get_serializer(instance)
        # Custom logic here, e.g., modify data or add additional fields
        data = serializer.data
        if event_obj:
            event_data = EventItem.objects.filter(book_id=self.kwargs['pk'])
            data['items'] = EventItemSerializer(event_data, many=True).data
        elif grocery_obj:
            grocery_data = OrderItem.objects.filter(book_id=self.kwargs['pk'])
            data['items'] = OrderItemSerializer(grocery_data, many=True).data
        elif room_obj:
            room_data = BookItem.objects.filter(book_id=self.kwargs['pk'])
            data['items'] = BookItemSerializer(room_data, many=True).data

        return Response(data)
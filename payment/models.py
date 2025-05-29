
from django.db import models

from accounts.models import User
from book.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator

from events.models import Event, EventPrice
from system.models import SoftDeletable


# Create your models here.
class Invoice(SoftDeletable):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    invoice_number = models.IntegerField(unique=True, auto_created=True, validators=[
        MinValueValidator(1000),
        MaxValueValidator(99999999)], )
    total_amount = models.DecimalField(max_digits=17, decimal_places=2)
    invoice_date = models.DateField(auto_now_add=True)
    discount = models.DecimalField(max_digits=17, decimal_places=2, default=0.0)
    billing_address = models.CharField(max_length=250)
    reference_id = models.CharField(max_length=250)
    payment_status = models.TextField()
    invoice_amount = models.DecimalField(max_digits=17, decimal_places=2)

    def __str__(self):
        return str(self.invoice_number)


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    event_price = models.ForeignKey(EventPrice, on_delete=models.RESTRICT)
    invoice = models.ForeignKey(Invoice,on_delete=models.RESTRICT)
    ticket_number = models.CharField(max_length=255, default="No Ticket")
    ticket_bought = models.BooleanField(default=False)
    ticket_img = models.ImageField(upload_to="ticket", default="ticket/ticket_pic.png")
    qr_img = models.ImageField(upload_to="qr", default="qr/ticket_pic.png")
    scanned = models.BooleanField(default=False)
    no_of_ticket = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event.title

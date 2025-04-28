
from django.db import models
from book.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Invoice(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    invoice_number = models.IntegerField(unique=True, auto_created=True, validators=[
        MinValueValidator(1000),
        MaxValueValidator(99999999)], )
    total_amount = models.DecimalField(max_digits=17, decimal_places=2)
    invoice_date = models.DateField(auto_now_add=True)
    discount = models.DecimalField(max_digits=17, decimal_places=2, default=0.0)
    billing_address = models.CharField(max_length=250)
    reference_id = models.CharField(max_length=250)
    payment_complete = models.BooleanField(default=False)
    invoice_amount = models.DecimalField(max_digits=17, decimal_places=2)

    def __str__(self):
        return self.invoice_number

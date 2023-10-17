from django.db import models
from decimal import Decimal

# Create your models here.

class Anonymisation(models.Model):
    class Meta:
        db_table = 'anonymisation"."anon'

    id = models.AutoField(primary_key=True)
    age = models.CharField(max_length=10)
    gender = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    citizenship = models.CharField(max_length=100)
    first_sum = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    second_sum = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    third_sum = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    fourth_sum = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    fifth_sum = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    first_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    second_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    third_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
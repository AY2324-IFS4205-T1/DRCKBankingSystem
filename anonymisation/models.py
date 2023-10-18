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


class Statistics(models.Model):
    class Meta:
        db_table = 'anonymisation"."stats'
    
    k_value = models.IntegerField(primary_key=True)
    utility_query1 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
    utility_query2 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
    info_loss = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
    set_k_value = models.BooleanField(default=False)
    first_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    second_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    third_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    fourth_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    fifth_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    first_balance_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    second_balance_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    third_balance_average = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))

    def set_k_value_to_true(self, k_value):
        for instance in Statistics.objects.all():
            instance.set_k_value = False
            instance.save()
            
        try:
            instance = Statistics.objects.get(k_value=k_value)
            instance.set_k_value = True
            instance.save()
            return True
        except Statistics.DoesNotExist:
            return False
from django.db import models
from django.core.validators import RegexValidator
from user.models import User

# Create your models here.
class Customer(models.Model):
    class Meta:
        db_table = 'customer"."customer_info'

    class Gender(models.TextChoices):
        FEMALE = "F"
        MALE = "M"	

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    identity_no = models.CharField(max_length=9, validators=[RegexValidator(regex='^[STFG]\d{7}[A-Z]$', message='Invalid Identity Number')])
    address = models.CharField(max_length=255)
    nationality = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=Gender.choices)
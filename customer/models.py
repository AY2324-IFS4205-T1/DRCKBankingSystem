from decimal import Decimal
import uuid

from django.core.validators import RegexValidator
from django.db import models

from user.models import User


# Create your models here.
class Customer(models.Model):
    class Meta:
        db_table = 'customer"."customer_info'

    class Gender(models.TextChoices):
        FEMALE = "Female"
        MALE = "Male"
        OTHERS = "Others"
    
    class Citizenship(models.TextChoices):
        CITIZEN = "Singaporean Citizen"
        PR = "Singaporean PR"
        NON_SINGAPOREAN = "Non-Singaporean"

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    identity_no = models.CharField(max_length=9, validators=[RegexValidator(regex='^[STFG][0-9]{7}[A-Z]$', message='Invalid Identity Number')])
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=6, validators=[RegexValidator(regex='^[0-9]{6}$', message='Invalid postal code')])
    citizenship = models.CharField(max_length=19, choices=Citizenship.choices)
    gender = models.CharField(max_length=6, choices=Gender.choices)


class AccountTypes(models.Model):
    class Meta:
        db_table = 'customer"."account_types'

    type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Accounts(models.Model):
    class Meta:
        db_table = 'customer"."accounts'
    
    class AccountStatus(models.TextChoices):
        ACTIVE = "Active"
        PENDING = "Pending"
        CLOSED = "Closed"

    account = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.ForeignKey(AccountTypes, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    status = models.CharField(max_length=7, choices=AccountStatus.choices)
    date_created = models.DateTimeField(auto_now_add=True)


class Transactions(models.Model):    
    class Meta:
        db_table = 'customer"."transactions'
    
    class TransactionTypes(models.TextChoices):
        DEPOSIT = "Deposit"
        WITHDRAWAL = "Withdrawal"
        TRANSFER = "Transfer"
    
    transaction = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=10, choices=TransactionTypes.choices)
    sender = models.ForeignKey(Accounts, related_name='sent_transactions', on_delete=models.CASCADE, null=True)
    recipient = models.ForeignKey(Accounts, related_name='received_transactions', on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.core.validators import RegexValidator
from user.models import User
import uuid

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


class AccountTypes(models.Model):
    class Meta:
        db_table = 'customer"."account_types'

    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Accounts(models.Model):
    class Meta:
        db_table = 'customer"."accounts'
    
    class AccountStatus(models.TextChoices):
        ACTIVE = "A"
        PENDING = "P"
        CLOSED = "C"

    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    type_id = models.ForeignKey(AccountTypes, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=1, choices=AccountStatus.choices)
    date_created = models.DateTimeField()


class Transactions(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.ForeignKey(Accounts, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient_id = models.ForeignKey(Accounts, related_name='received_transactions', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField()
    
    class Meta:
        db_table = 'customer"."transactions'
        
    def clean_account(self):
        if self.sender_id == self.recipient_id:
            raise ValueError("Sender account should not be recipient account")
    def clean_amount(self):
        if self.type in ['W'] and self.amount > self.sender_id.balance:
            raise ValueError("Withdrawal amount is too much")
        elif self.type in ['T'] and self.amount > self.sender_id.balance:
            raise ValueError("Transfer amount is too much")
	
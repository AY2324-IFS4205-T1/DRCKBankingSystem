from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
import re

class AppUserManager(BaseUserManager):
	def create_user(self, email, password=None):
		if not email:
			raise ValueError('An email is required.')
		if not password:
			raise ValueError('A password is required.')
		email = self.normalize_email(email)
		user = self.model(email=email)
		user.set_password(password)
		user.save()
		return user
	def create_superuser(self, email, password=None):
		if not email:
			raise ValueError('An email is required.')
		if not password:
			raise ValueError('A password is required.')
		user = self.create_user(email, password)
		user.is_superuser = True
		user.save()
		return user


class AppUser(AbstractBaseUser, PermissionsMixin):
	user_id = models.AutoField(primary_key=True)
	email = models.EmailField(max_length=50, unique=True)
	username = models.CharField(max_length=50)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	objects = AppUserManager()
	def __str__(self):
		return self.username
	
# Enums
class AuthUserType(models.TextChoices):
	CUSTOMER = "C"
	STAFF = "S"

class Gender(models.TextChoices):
    FEMALE = "F"
    MALE = "M"	

class AccountStatus(models.TextChoices):
    ACTIVE = "A"
    PENDING = "P"
    CLOSED = "C"

class Type(models.TextChoices):
    DEPOSIT = "D"
    WITHDRAW = "W"
    TRANSFER = "T"

class TicketStatus(models.TextChoices):
    CLOSED = "C"
    OPEN = "O"
    APPROVED = "A"


# Customer Schema
class Customers(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    identity_no = models.CharField(max_length=9)
    address = models.CharField(max_length=255)
    nationality = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    def clean(self):
	    if not re.match(r'^[STFG]\d{7}[A-Z]$'):
		    raise ValueError("Invalid Identity Number")

class AccountTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

class Accounts(models.Model):
	account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user_id = models.ForeignKey(Customers, on_delete=models.CASCADE)
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
	def clean_account(self):
		if self.sender_id == self.recipient_id:
			raise ValueError("Sender account should not be recipient account")
	def clean_amount(self):
		if self.type in ['W'] and self.amount > self.sender_id.balance:
			raise ValueError("Withdrawal amount is too much")
		elif self.type in ['T'] and self.amount > self.sender_id.balance:
			raise ValueError("Transfer amount is too much")
	

# Staff Schema
class Departments(models.Model):
	department_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255)

class Staff(models.Model):
	user_id = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	title = models.CharField(max_length=255)
	birth_date = models.DateField()
	gender = models.CharField(max_length=1, choices=Gender.choices)
	
class DeptManager(models.Model):
	department_id = models.ForeignKey(Departments, on_delete=models.CASCADE)
	user_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
	start_date = models.DateField()
	end_date = models.DateField(null=True)
	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['department_id', 'user_id'], name='dept_manager_unique'),
			models.CheckConstraint(check=models.Q(end_date__isnull=True) | models.Q(end_date__gt=models.F('start_date')), name='end_date_check'),
        ]
	
class TicketTypes(models.Model):
    ticket_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    department_id = models.ForeignKey(Departments, null=True, on_delete=models.CASCADE)


class Tickets(models.Model):
	ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	ticket_type_id = models.ForeignKey(TicketTypes, on_delete=models.PROTECT)
	status = models.CharField(max_length=1, choices=TicketStatus.choices)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tickets', on_delete=models.PROTECT)
	created_date = models.DateTimeField()
	closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='closed_tickets', on_delete=models.PROTECT)
	closed_date = models.DateTimeField(null=True)
	class Meta:
		constraints = [
            models.CheckConstraint(check=models.Q(closed_date__isnull=True) | models.Q(closed_date__gt=models.F('created_date')), name='closed_date_check'),
        ]

class TicketMessage(models.Model):
	ticket_id = models.ForeignKey(Tickets, on_delete=models.CASCADE)
	message_id = models.IntegerField()
	user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	message = models.CharField()
	date = models.DateTimeField()
	class Meta:
		constraints = [
            models.UniqueConstraint(fields=['ticket_id', 'message_id'], name='ticket_msg_unique'),
        ]

# Log Schema
class LogAccount(models.Model):
	id = models.AutoField(primary_key=True)
	user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	time = models.DateTimeField()
	ip = models.GenericIPAddressField(protocol='both')

class LogCalls(models.Model):
	id = models.IntegerField(primary_key=True)
	user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	time = models.DateTimeField()
	action = models.CharField(max_length=255)
	
	
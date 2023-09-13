from django.db import models
from customer.models import AccountTypes, Customer
from user.models import User
import uuid

# Create your models here.
class Staff(models.Model):
    class Meta:
        db_table = 'staff"."staff_info'

    class Gender(models.TextChoices):
        FEMALE = "F"
        MALE = "M"	

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)

class TicketTypes(models.Model):
    class Meta:
        db_table = 'staff"."ticket_types'

    ticket_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

class Tickets(models.Model):
    class Meta:
        db_table = 'staff"."tickets'
        constraints = [
            models.CheckConstraint(check=models.Q(closed_date__isnull=True) | models.Q(closed_date__gt=models.F('created_date')), name='closed_date_check'),
        ]
        
    class TicketStatus(models.TextChoices):
        CLOSED = "C"
        OPEN = "O"
        APPROVED = "A"
    
    ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_type = models.ForeignKey(TicketTypes, on_delete=models.PROTECT, null=True)
    account_type = models.ForeignKey(AccountTypes, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=TicketStatus.choices)
    created_by = models.ForeignKey(Customer, related_name='created_tickets', on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    closed_by = models.ForeignKey(Staff, related_name='closed_tickets', on_delete=models.PROTECT, null=True)
    closed_date = models.DateTimeField(null=True)
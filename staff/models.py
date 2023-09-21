import uuid

from django.db import models

from customer.models import AccountTypes, Customer
from user.models import User


# Create your models here.
class Staff(models.Model):
    class Meta:
        db_table = 'staff"."staff_info'

    class Gender(models.TextChoices):
        FEMALE = "Female"
        MALE = "Male"
        OTHERS = "Others"

    class Title(models.TextChoices):
        REVIEWER = "Ticket Reviewer"
        SECURITY = "Security Engineer"
        RESEARCHER = "Researcher"

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=17, choices=Title.choices)
    birth_date = models.DateField()
    gender = models.CharField(max_length=6, choices=Gender.choices)


class Tickets(models.Model):
    class Meta:
        db_table = 'staff"."tickets'
        constraints = [
            models.CheckConstraint(check=models.Q(closed_date__isnull=True) | models.Q(closed_date__gt=models.F('created_date')), name='closed_date_check'),
        ]
        
    class TicketType(models.TextChoices):
        OPEN_ACCOUNT = "Opening Account"
        CLOSE_ACCOUNT = "Closing Account"
        
    class TicketStatus(models.TextChoices):
        OPEN = "Open"
        APPROVED = "Approved"
        REJECTED = "Rejected"

    
    ticket = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_type = models.CharField(max_length=15, choices=TicketType.choices)
    account_type = models.ForeignKey(AccountTypes, on_delete=models.PROTECT)
    status = models.CharField(max_length=8, choices=TicketStatus.choices)
    created_by = models.ForeignKey(Customer, related_name='created_tickets', on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    closed_by = models.ForeignKey(Staff, related_name='closed_tickets', on_delete=models.PROTECT, null=True)
    closed_date = models.DateTimeField(null=True)

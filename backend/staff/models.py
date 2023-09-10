from django.db import models
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


class Departments(models.Model):
    class Meta:
        db_table = 'staff"."departments'
    
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class DeptManager(models.Model):
    class Meta:
        db_table = 'staff"."dept_manager'
        constraints = [
            models.UniqueConstraint(fields=['department_id', 'user_id'], name='dept_manager_unique'),
            models.CheckConstraint(check=models.Q(end_date__isnull=True) | models.Q(end_date__gt=models.F('start_date')), name='end_date_check'),
        ]
    
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True)


class TicketTypes(models.Model):
    class Meta:
        db_table = 'staff"."ticket_types'

    ticket_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    department_id = models.ForeignKey(Departments, null=True, on_delete=models.CASCADE)


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
    # Will review this another day
    ticket_type_id = models.ForeignKey(TicketTypes, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=TicketStatus.choices)
    created_by = models.ForeignKey(Staff, related_name='created_tickets', on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    closed_by = models.ForeignKey(Staff, related_name='closed_tickets', on_delete=models.PROTECT)
    closed_date = models.DateTimeField(null=True)


# Log Schema
# class LogAccount(models.Model):
#     class Meta:
#         db_table = 'staff"."log_accounts'

#     id = models.AutoField(primary_key=True)
#     user_id = models.ForeignKey(User, on_delete=models.PROTECT)
#     time = models.DateTimeField()
#     ip = models.GenericIPAddressField(protocol='both')


# class LogCalls(models.Model):
#     class Meta:
#         db_table = 'staff"."log_calls'

#     id = models.IntegerField(primary_key=True)
#     user_id = models.ForeignKey(User, on_delete=models.PROTECT)
#     time = models.DateTimeField()
#     action = models.CharField(max_length=255)
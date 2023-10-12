from django.db import models

from user.models import User
from customer.models import Transactions

# Create your models here
class Severity(models.TextChoices):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class APIMethod(models.TextChoices):
    GET = "GET"
    POST = "POST"

class LoginLog(models.Model):
    class Meta:
        db_table = 'log"."login_log'

    id = models.AutoField(primary_key=True)
    level = models.CharField(max_length=6, choices=Severity.choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_success = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()

class APILog(models.Model):
    class Meta:
        db_table = 'log"."api_log'

    id = models.AutoField(primary_key=True)
    level = models.CharField(max_length=6, choices=Severity.choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    api = models.TextField()
    method = models.CharField(max_length=4, choices=APIMethod.choices)
    ip = models.GenericIPAddressField()

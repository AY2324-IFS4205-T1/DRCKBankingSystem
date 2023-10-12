from django.db import models

from user.models import User
from customer.models import Transactions

# Create your models here
class Severity(models.TextChoices):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Information"

class APIMethod(models.TextChoices):
    GET = "GET"
    POST = "POST"

class LoginLog(models.Model):
    class Meta:
        db_table = 'log"."login_log'

    id = models.AutoField(primary_key=True)
    login_type = models.CharField(max_length=8, choices=User.user_type.choices)
    is_success = models.BooleanField()
    username = models.CharField(max_length=150, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ip = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    count = models.SmallIntegerField()
    level = models.CharField(max_length=11, choices=Severity.choices)

class APILog(models.Model):
    class Meta:
        db_table = 'log"."api_log'

    id = models.AutoField(primary_key=True)
    level = models.CharField(max_length=11, choices=Severity.choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    api = models.TextField()
    method = models.CharField(max_length=4, choices=APIMethod.choices)
    ip = models.GenericIPAddressField()

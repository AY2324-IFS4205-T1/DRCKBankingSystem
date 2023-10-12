from django.db import models
from staff.models import Staff

from user.models import User

# Create your models here
class Severity(models.TextChoices):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Information"


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
    severity = models.CharField(max_length=11, choices=Severity.choices)


class AccessControlLogs(models.Model):
    class Meta:
        db_table = 'log"."access_control_log'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_permission_type = models.CharField(choices=list(User.user_type.choices)+list(Staff.Title.choices))
    user_violation_count = models.SmallIntegerField()
    api_permission_type = models.CharField(choices=list(User.user_type.choices)+list(Staff.Title.choices))
    api_view_name = models.TextField()
    ip = models.GenericIPAddressField()
    ip_violation_count = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=11, choices=Severity.choices)

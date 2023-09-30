from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, phone_no, type, password=None):        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            phone_no=phone_no,
            type=type
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        unique_together = [["username","type"]]
        
    class user_type(models.TextChoices):
        CUSTOMER = "Customer"
        STAFF = "Staff"

    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    email = models.EmailField()
    phone_no = models.CharField(max_length=8)
    type = models.CharField(max_length=8, choices=user_type.choices)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["phone_no", "type", "date_joined", "last_login", "is_active"]


class TwoFA(models.Model):
    class Meta:
        db_table = "two_fa"

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    key = models.CharField(max_length=32)
    last_authenticated = models.DateTimeField(null=True)
    knox_token = models.CharField(max_length=64, blank=True)
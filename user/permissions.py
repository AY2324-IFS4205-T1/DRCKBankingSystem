from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions

from user.models import TwoFA


class IsTwoFactorAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        try:
            two_fa = TwoFA.objects.get(user=request.user)
        except Exception:
            self.message = "User does not have 2FA set up."
            return False
    
        self.message = "User is not 2FA authenticated."
        if two_fa.last_authenticated == None:
            return False

        difference = timezone.now() - two_fa.last_authenticated
        is_two_fa_authenticated = difference < timedelta(minutes=15)

        if is_two_fa_authenticated:
            two_fa.last_authenticated = timezone.now()
        else:
            two_fa.last_authenticated = None

        two_fa.save()
        return is_two_fa_authenticated

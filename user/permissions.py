from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions

from user.models import TwoFA


class IsTwoFactorAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        two_fa = TwoFA.objects.get(user=request.user)
        if not two_fa.last_authenticated:
            return False

        difference = timezone.now() - two_fa.last_authenticated
        is_two_fa_authenticated = difference < timedelta(minutes=15)

        if is_two_fa_authenticated:
            two_fa.last_authenticated = timezone.now()
        else:
            two_fa.last_authenticated = None

        two_fa.save()
        return is_two_fa_authenticated

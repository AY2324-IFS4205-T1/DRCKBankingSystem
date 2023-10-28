from django.db import transaction
from rest_framework.permissions import BasePermission

from user.models import TwoFA


class HasNotSetupTwoFA(BasePermission):

    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        try:
            two_fa = TwoFA.objects.get(user=request.user)
        except TwoFA.DoesNotExist:
            return True
        return two_fa.knox_token == ""

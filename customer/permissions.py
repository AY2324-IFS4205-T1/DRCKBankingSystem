from django.db import transaction
from rest_framework import permissions

from log.logging import AccessControlLogger
from user.models import User


class IsCustomer(permissions.BasePermission):

    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        permission_granted = request.user.type == User.user_type.CUSTOMER
        if not permission_granted:
            AccessControlLogger(request, User.user_type.CUSTOMER, view.get_view_name())
        return permission_granted
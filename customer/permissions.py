from rest_framework import permissions

from user.models import User


class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.type == User.user_type.CUSTOMER
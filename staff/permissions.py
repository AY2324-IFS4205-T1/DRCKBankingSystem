from django.db import transaction
from rest_framework.permissions import BasePermission

from log.logging import AccessControlLogger
from staff.models import Staff
from user.models import User


class IsStaff(BasePermission):

    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        permission_granted = request.user.type == User.user_type.STAFF
        if not permission_granted:
            AccessControlLogger(request, User.user_type.STAFF, view.get_view_name())
        return permission_granted

class IsTicketReviewer(BasePermission):
    
    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        staff = Staff.objects.get(user=request.user)
        permission_granted = staff.title == Staff.Title.REVIEWER
        if not permission_granted:
            AccessControlLogger(request, Staff.Title.REVIEWER, view.get_view_name())
        return permission_granted

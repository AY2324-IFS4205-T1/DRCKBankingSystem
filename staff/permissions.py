from rest_framework.permissions import BasePermission
from staff.models import Staff

from user.models import User


class IsStaff(BasePermission):

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.type == User.user_type.STAFF

class IsTicketReviewer(BasePermission):
    
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = Staff.objects.get(user=request.user)
        return user.title == Staff.Title.REVIEWER
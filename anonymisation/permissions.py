from rest_framework.permissions import BasePermission

from staff.models import Staff
from user.models import User


class IsResearcher(BasePermission):
    
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = Staff.objects.get(user=request.user)
        return user.title == Staff.Title.RESEARCHER
    
class IsAnonymiser(BasePermission):
    
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = Staff.objects.get(user=request.user)
        return user.title == Staff.Title.ANONYMISER
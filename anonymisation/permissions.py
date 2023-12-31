from django.db import transaction
from rest_framework.permissions import BasePermission

from log.logging import AccessControlLogger
from staff.models import Staff


class IsResearcher(BasePermission):
    
    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        staff = Staff.objects.get(user=request.user)
        permission_granted = staff.title == Staff.Title.RESEARCHER
        if not permission_granted:
            AccessControlLogger(request, Staff.Title.RESEARCHER, view.get_view_name())
        return permission_granted


class IsAnonymiser(BasePermission):
    
    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        staff = Staff.objects.get(user=request.user)
        permission_granted = staff.title == Staff.Title.ANONYMISER
        if not permission_granted:
            AccessControlLogger(request, Staff.Title.ANONYMISER, view.get_view_name())
        return permission_granted


class IsResearcherOrAnonymiser(BasePermission):
    
    @transaction.atomic
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        staff = Staff.objects.get(user=request.user)
        permission_granted = staff.title in [Staff.Title.RESEARCHER, Staff.Title.ANONYMISER]
        if not permission_granted:
            AccessControlLogger(request, Staff.Title.RESEARCHER, view.get_view_name())
            AccessControlLogger(request, Staff.Title.ANONYMISER, view.get_view_name())
        return permission_granted
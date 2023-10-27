from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from log.permissions import IsAuditor
from log.serializers import (AccessControlLoggingSerializer,
                             ConflictOfInterestLoggingSerializer,
                             LoginLoggingSerializer)
from staff.permissions import IsStaff
from user.authentication import TokenAndTwoFactorAuthentication


# Create your views here.
class LoginLoggingView(APIView):
    """Post request
    The Login Logs records all login attempts.
    Logs are marked with higher severity if:
        1) Login attempt was unsuccessful.
        2) Many unsuccessful attempts were executed within a short timeframe (5 minutes).
        3) Unsuccessful attempt were made after a successful login from a different IP address.

    Args:
        severity: ("High", "Medium", "Low") defaults to None which returns all
        start: datetime string defaults to 1 day ago (e.g. 2023-10-28T01:30)
        end: datetime string defaults to now (e.g. 2023-10-28T01:30)

    Returns:
        List of login logs capped at the first 100
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAuditor)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = LoginLoggingSerializer(
            request.user, request.data, data=request.data
        )
        if serializer.is_valid():
            serializer = serializer.get_logs()
            return Response({"login_logs": serializer}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessControlLoggingView(APIView):
    """Post request
    The AccessControl Logs records all unauthorised attempts to access an API.
    Logs are marked with higher severity if:
        1) Multiple attempts were made by the same user.
        2) Multiple attempts were made by the same IP address.

    Args:
        severity: ("High", "Medium", "Low") defaults to None
        start: datetime string defaults to 1 day ago (e.g. 2023-10-28T01:30)
        end: datetime string defaults to now (e.g. 2023-10-28T01:30)

    Returns:
        List of access control logs capped at the first 100
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAuditor)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = AccessControlLoggingSerializer(
            request.user, request.data, data=request.data
        )
        if serializer.is_valid():
            serializer = serializer.get_logs()
            return Response(
                {"access_control_logs": serializer}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConflictOfInterestLoggingView(APIView):
    """Post request
    The ConflictOfInterest Logs records all approval of customer tickets.
    Its main purpose is to identify a staff using their permissions as a staff to approve a ticket that they opened as a customer.
    Logs are marked with higher severity if for each ticket:
        1) The usernames of the customer and staff are the same.
        2) The IP addresses of the customer and staff are the same.

    Args:
        severity: ("High", "Medium", "Low") defaults to None
        start: datetime string defaults to 1 day ago (e.g. 2023-10-28T01:30)
        end: datetime string defaults to now (e.g. 2023-10-28T01:30)

    Returns:
        List of conflict of interest logs capped at the most recent 100
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAuditor)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = ConflictOfInterestLoggingSerializer(
            request.user, request.data, data=request.data
        )
        if serializer.is_valid():
            serializer = serializer.get_logs()
            return Response(
                {"conflict_interest_logs": serializer}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from log.permissions import IsAuditor
from log.serializers import LoggingSerializer

from staff.permissions import IsStaff
from user.authentication import TokenAndTwoFactorAuthentication


# Create your views here.
class LoginLoggingView(APIView):
    """Post request

    Args:
        severity: ("High", "Medium", "Low") defaults to None which returns all
        start: datetime string defaults to 1 day ago (e.g. 2023-10-28T01:30)
        end: datetime string defaults to now (e.g. 2023-10-28T01:30)

    Returns:
        List of login logs capped at the last 100
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAuditor)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def post(self, request):
        serializer = LoggingSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_login_logs()
            return Response({"login_logs": serializer}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APILoggingView(APIView):
    """Post request

    Args:
        severity: ("High", "Medium", "Low") defaults to None
        start: datetime string defaults to 1 day ago (e.g. 2023-10-28T01:30)
        end: datetime string defaults to now (e.g. 2023-10-28T01:30)

    Returns:
        List of API logs
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAuditor)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def post(self, request):
        serializer = LoggingSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_api_logs()
            return Response({"api_logs": serializer}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

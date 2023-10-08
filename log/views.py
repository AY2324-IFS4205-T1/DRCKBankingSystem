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

    Returns:

    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAuditor)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def post(self, request):
        serializer = LoggingSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_logs()
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

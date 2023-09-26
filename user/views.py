from django.http import FileResponse

from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from knox.auth import TokenAuthentication

from user.serializers import GetTwoFASerializer, VerifyTwoFASerializer

# Create your views here.
class AuthenticationTypeCheckView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    # Check if user is authenticated and see if the database user type and request user type matches
    def get(self, request):
        # Retrieves the request user type
        input_user_type = request.headers['Type']
        if input_user_type != self.request.user.type:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(status=status.HTTP_200_OK)
    
# Create your views here.
class SetupTwoFactorAuthenticationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        qr_code = GetTwoFASerializer(request.user).get_qr_code()
        return FileResponse(qr_code, content_type="image/png")


class VerifyTwoFactorAuthenticationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = VerifyTwoFASerializer(
            request.user, request.data, data=request.data
        )
        if serializer.is_valid():
            result = {"result": serializer.verify()}
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
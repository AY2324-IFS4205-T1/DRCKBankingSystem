from django.http import FileResponse
from knox.auth import TokenAuthentication
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import GetTwoFASerializer, VerifyTwoFASerializer


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

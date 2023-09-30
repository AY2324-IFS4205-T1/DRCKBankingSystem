from django.http import FileResponse

from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from knox.auth import TokenAuthentication
from knox.views import LogoutView as KnoxLogoutView

from user.serializers import GetTwoFASerializer, RemoveTwoFASerializer, VerifyTwoFASerializer

class AuthenticationTypeCheckView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"user_type": request.user.type}, status=status.HTTP_200_OK)


class LogoutView(KnoxLogoutView):
    def post(self, request, format=None):
        RemoveTwoFASerializer(request.user)
        return super().post(request, format)


class SetupTwoFactorAuthenticationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        qr_code = GetTwoFASerializer(request.user).get_qr_code()
        return FileResponse(qr_code, content_type="image/png")


class VerifyTwoFactorAuthenticationView(APIView):
    '''
    otp: 12345678
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = VerifyTwoFASerializer(
            request.user, request.data, request.headers.get('Authorization'), data=request.data
        )
        if serializer.is_valid():
            json_result = serializer.verify()
            return Response(json_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

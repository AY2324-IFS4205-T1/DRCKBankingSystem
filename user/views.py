from django.http import FileResponse
from knox.auth import TokenAuthentication
from knox.views import LogoutView as KnoxLogoutView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from ipware import IpWare

from user.serializers import (AuthCheckSerializer, GetTwoFASerializer,
                              RemoveTwoFASerializer, VerifyTwoFASerializer)


class LogoutView(KnoxLogoutView):
    def post(self, request, format=None):
        RemoveTwoFASerializer(request.user)
        request.user.auth_token_set.all().delete()
        return super().post(request, format)


class SetupTwoFactorAuthenticationView(APIView):
    """Get Request

    Returns:
        FileReponse
    """
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "sensitive_request"

    def get(self, request):
        qr_code = GetTwoFASerializer(request.user).get_qr_code()
        return FileResponse(qr_code, content_type="image/png")


class VerifyTwoFactorAuthenticationView(APIView):
    """Post Request

    Args:
        otp: 8 digit string/number

    Returns:
        2FA success: True/False
        last_authenticated: timestamp
    """
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "non_sensitive_request"

    def post(self, request):
        serializer = VerifyTwoFASerializer(request.user, request.data, request.headers.get('Authorization'), data=request.data)
        if serializer.is_valid():
            json_result = serializer.verify()
            return Response(json_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthenticationCheckView(APIView):
    """Post Request

    Args:
        page_type: string, options are: ["Customer", "Staff", "Ticket Reviewer", "Auditor", "Researcher"]

    Returns:
        authenticated: True/False
        authenticated_message: string, options are ["User not logged in.", "The session has changed, 2FA needs to be verified again.", "2FA has not been verified.", "2FA timeout, 2FA needs to be verified again."]
        authorised: True/False
        user_authorisation: string, options are ["Customer", "Ticket Reviewer", "Auditor", "Researcher"]
    """
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serialiser = AuthCheckSerializer(request, data=request.data)
        if serialiser.is_valid():
            response = serialiser.get_response()
            if response["authenticated"] and response["authorised"]:
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(response, status=status.HTTP_403_FORBIDDEN)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

class GetIPTestingView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        proxy_count = 6
        ip = None
        trusted_route = None
        while ip == None:
            proxy_count -= 1
            if proxy_count < 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            ipw = IpWare(proxy_count=proxy_count)
            ip, trusted_route = ipw.get_client_ip(meta=request.META)
        response = {"ip exploded": ip.exploded, "proxy_count": proxy_count, "trusted_route": trusted_route}
        return Response(response, status=status.HTTP_200_OK)

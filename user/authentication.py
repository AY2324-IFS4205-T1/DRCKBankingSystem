from django.contrib.auth import get_user_model
from django.utils import timezone
from knox.auth import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from main.settings import REST_KNOX
from user.models import TwoFA

# https://reintech.io/blog/writing-custom-authentication-backend-django


class UserAuth:
    def authenticate(self, _, username=None, password=None, type=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username, type=type)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None


class TokenAndTwoFactorAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token_authenticated = super().authenticate(request)
        if token_authenticated == None:
            return None

        user = token_authenticated[0]
        token = request.headers.get("Authorization")[6:]
        try:
            two_fa = TwoFA.objects.get(user=user)
        except Exception:
            raise AuthenticationFailed("User does not have 2FA set up.")
        
        if not two_fa.knox_token: # if token is not set up, assume that 2FA is not set up
            raise AuthenticationFailed("User does not have 2FA set up.")

        if token != two_fa.knox_token:
            raise AuthenticationFailed("2FA has not been verified.")
        
        return token_authenticated

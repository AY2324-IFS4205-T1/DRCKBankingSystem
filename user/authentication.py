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

        if token != two_fa.knox_token:
            raise AuthenticationFailed("The session has changed, 2FA needs to be verified again.")

        if two_fa.last_authenticated == None:
            raise AuthenticationFailed("2FA has not been verified.")

        difference = timezone.now() - two_fa.last_authenticated
        is_two_fa_authenticated = difference < REST_KNOX["TOKEN_TTL"]

        if is_two_fa_authenticated:
            delta = (timezone.now() + REST_KNOX["TOKEN_TTL"] - two_fa.last_authenticated).total_seconds()
            if delta > REST_KNOX["MIN_REFRESH_INTERVAL"]:
                two_fa.last_authenticated = timezone.now()
                two_fa.save()
            return token_authenticated
        else:
            two_fa.last_authenticated = None
            two_fa.save()
            raise AuthenticationFailed("2FA timeout, 2FA needs to be verified again.")

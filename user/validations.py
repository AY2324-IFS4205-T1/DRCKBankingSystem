from django.core import exceptions
from django.forms import ValidationError

from .models import TwoFA


def validate_otp(json_dict):
    try:
        otp = json_dict["otp"]
    except KeyError:
        raise ValidationError("Field 'otp' missing.")
    if len(str(otp)) != 8:
        raise ValidationError("OTP is not 8 characters long.")
    try:
        int(str(otp))
    except ValueError:
        raise ValidationError("OTP does not have 8 digits.")
    return str(otp)

def validate_user_2fa(user):
    try:
        two_fa = TwoFA.objects.get(user=user)
    except exceptions.ObjectDoesNotExist:
        raise ValidationError("User does not have 2FA set up.")
    return two_fa
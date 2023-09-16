import decimal
from django.core import exceptions
from rest_framework.serializers import ValidationError

from customer.models import AccountTypes, Accounts


def validate_account_type(account_type):
    try:
        account_type = AccountTypes.objects.get(name=account_type)
    except exceptions.ObjectDoesNotExist:
        raise ValidationError("Account type given does not exist.")
    return account_type

def validate_account(account_id):
    try:
        account = Accounts.objects.get(account=account_id)
    except exceptions.ValidationError as validation_error:
        if "is not a valid UUID" in validation_error.message:
            raise ValidationError("Account ID does not exist.")
        else:
            raise validation_error
    return account

def validate_amount(amount):
    try:
        amount = float(amount)
    except Exception:
        raise ValidationError("Amount is not a number.")
    rounded = round(amount)
    if rounded != amount:
        raise ValidationError("Amount can only have a maximum of 2 decimal places.")
    if amount == 0:
        raise ValidationError("Amount cannot be 0.")
    decimal.getcontext().prec = 2
    return decimal.Decimal(amount)

def validate_description(description):
    description = str(description)
    if len(description) > 255:
        raise ValidationError("Description cannot be longer than 255 characters")
    return description

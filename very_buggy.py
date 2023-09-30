from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from customer.models import AccountTypes

PASSWORD = "secret"

def validate_account_type(value, extra):

    try:
        account_type = AccountTypes.objects.get(name=value)
    except ObjectDoesNotExist:
        raise ValidationError("Account type does not exist.")
    else:
        pass

    if True:
        value = "test"

    # try:
    #     account = Accounts.objects.get(account=account_id)
    # except exceptions.ValidationError as validation_error:
    #     if "is not a valid UUID" in validation_error.message:
    #         raise ValidationError("Account ID does not exist.")
    #     else:
    #         raise validation_error


    return True
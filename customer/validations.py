import decimal

from django.core import exceptions
from rest_framework.serializers import ValidationError

from customer.models import Accounts, AccountTypes, Customer
from staff.models import Tickets


def validate_account_type(json_dict):
    try:
        account_type = json_dict["account_type"]
    except KeyError:
        raise ValidationError("Field 'account_type' missing.")
    
    try:
        account_type = AccountTypes.objects.get(name=account_type)
    except exceptions.ObjectDoesNotExist:
        raise ValidationError("Account type given does not exist.")
    
    return account_type


def validate_no_repeated_application(customer, account_type):
    open_tickets = Tickets.objects.filter(created_by=customer, account_type=account_type, status=Tickets.TicketStatus.OPEN)
    if len(open_tickets) != 0:
        raise ValidationError("Customer has already applied for this account type.")


def validate_account(json_dict, id_type="account_id"):
    try:
        account_id = json_dict[id_type]
    except KeyError:
        raise ValidationError("Field '" + id_type + "' is missing.")
    
    try:
        account = Accounts.objects.get(account=account_id)
    except exceptions.ValidationError as validation_error:
        if "is not a valid UUID" in validation_error.message:
            raise ValidationError("Account ID does not exist.")
        else:
            raise validation_error
    return account

def validate_amount(json_dict):
    try:
        amount = json_dict["amount"]
    except KeyError:
        raise ValidationError("Field 'amount' missing.")
    
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

def validate_description(json_dict):
    try:
        description = json_dict["description"]
    except KeyError:
        raise ValidationError("Field 'description' missing.")
    
    description = str(description)
    if len(description) > 255:
        raise ValidationError("Description cannot be longer than 255 characters")
    return description

def validate_account_owner(user_id, account):
    customer = Customer.objects.get(user = user_id)
    user_accounts = Accounts.objects.filter(user=customer)
    if account not in user_accounts:
        raise ValidationError("Account does not belong to the user.")
    return True

def validate_sufficient_amount(account, amount):
    if amount > account.balance:
        raise ValidationError("Insufficient value in account.")
    return True

def validate_sender_recipient(sender, recipient):
    if sender == recipient:
        raise ValidationError("Unable to transfer money to self.")
    return True

def validate_total_balance(initial_balance, sender_balance, recipient_balance):
    if initial_balance != (sender_balance + recipient_balance):
        raise ValidationError("Error in transfer calculation.")
    return True

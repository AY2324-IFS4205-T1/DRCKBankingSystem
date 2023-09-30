import decimal
from datetime import datetime

from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from customer.models import Accounts, AccountTypes, Customer
from staff.models import RequestCloseAccount, RequestOpenAccount, Tickets


def validate_nric_and_citizenship(nric, citizenship, birth_date):
    error_message = "Incorrect input in field 'identity_no'."

    if citizenship in [Customer.Citizenship.CITIZEN, Customer.Citizenship.PR]:
        if nric[0] not in ["S", "T"]:
            raise ValidationError(error_message)
        if (
            datetime.strptime(birth_date, "%Y-%m-%d") < datetime(2000, 1, 1)
            and nric[0] != "S"
        ):
            raise ValidationError(error_message)
        if (
            datetime.strptime(birth_date, "%Y-%m-%d") >= datetime(2000, 1, 1)
            and nric[0] != "T"
        ):
            raise ValidationError(error_message)
    else:
        if nric[0] not in ["F", "G", "M"]:
            raise ValidationError(error_message)


def validate_ticket_input(json_dict):
    try:
        ticket_type = json_dict["ticket_type"]
    except KeyError:
        raise ValidationError("Field 'ticket_type' missing.")
    
    if ticket_type not in Tickets.TicketType.values:
        raise ValidationError("Ticket type given does not exist.")

    try:
        value = json_dict["value"]
    except KeyError:
        raise ValidationError("Field 'value' missing.")
    
    return ticket_type, value


def validate_account_type(value):
    try:
        account_type = AccountTypes.objects.get(name=value)
    except ObjectDoesNotExist:
        raise ValidationError("Account type given does not exist.")
    return account_type
        


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


def validate_account_owner(user_id, account):
    customer = Customer.objects.get(user=user_id)
    user_accounts = Accounts.objects.filter(user=customer)
    if account not in user_accounts:
        raise ValidationError("Account does not belong to the user.")
    return True


def validate_no_repeated_ticket(customer, ticket_type, value):
    if ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
        for requests in RequestOpenAccount.objects.filter(ticket__created_by=customer, ticket__ticket_type=ticket_type, ticket__status=Tickets.TicketStatus.OPEN):
            if requests.account_type == value:
                raise ValidationError("Customer has already applied for this account type.")
    if ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
        for requests in RequestCloseAccount.objects.filter(ticket__created_by=customer, ticket__ticket_type=ticket_type, ticket__status=Tickets.TicketStatus.OPEN):
            if requests.account_id == value:
                raise ValidationError("Customer has already requested to close this account.")
    return True


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

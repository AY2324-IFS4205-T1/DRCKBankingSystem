import decimal
from datetime import datetime

from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from customer.models import Accounts, AccountTypes, Customer
from staff.models import RequestCloseAccount, RequestOpenAccount, Tickets

MAX_ACCOUNT_BALANCE = decimal.Decimal("9999999999.99")


def validate_name_length(name):
    if len(name) <= 100:
        return True
    raise ValidationError("The length of name provided must be of length 100 characters or less.")


def validate_address_length(address):
    if len(address) <= 255:
        return True
    raise ValidationError("The length of address provided must be of length 255 characters or less.")


def validate_nric_and_citizenship(nric, citizenship, birth_date):
    id_citizenship_error = "Identity number does not match the Citizenship provided."
    id_dob_error = "Identity number does not match the Date of Birth provided."

    if citizenship in [Customer.Citizenship.CITIZEN, Customer.Citizenship.PR]:
        if nric[0] not in ["S", "T"]:
            raise ValidationError(id_citizenship_error)
        if (
            datetime.strptime(birth_date, "%Y-%m-%d") < datetime(2000, 1, 1)
            and nric[0] != "S"
        ):
            raise ValidationError(id_dob_error)
        if (
            datetime.strptime(birth_date, "%Y-%m-%d") >= datetime(2000, 1, 1)
            and nric[0] != "T"
        ):
            raise ValidationError(id_dob_error)
    else:
        if nric[0] not in ["F", "G", "M"]:
            raise ValidationError(id_citizenship_error)


def validate_ticket_input(json_dict):
    try:
        ticket_type = json_dict["ticket_type"].strip()
    except KeyError:
        raise ValidationError("Please input the ticket type.")
    
    if ticket_type not in Tickets.TicketType.values:
        raise ValidationError("Ticket type given does not exist.")

    try:
        value = json_dict["value"].strip()
    except KeyError:
        raise ValidationError("Please input the value.")
    
    return ticket_type, value


def validate_account_type(value):
    try:
        value = int(value)
    except ValueError:
        raise ValidationError("Account type should be a number.")
    try:
        account_type = AccountTypes.objects.get(type=value)
    except ObjectDoesNotExist:
        raise ValidationError("Account type given does not exist.")
    return account_type
        


def validate_account(json_dict, id_type="account_id"):
    try:
        account_id = json_dict[id_type].strip()
    except KeyError:
        raise ValidationError("Please input the account ID.")

    try:
        account = Accounts.objects.get(account=account_id)
    except exceptions.ValidationError as validation_error:
        if "is not a valid UUID" in validation_error.message:
            raise ValidationError("Account ID provided does not exist.")
        else:
            raise validation_error
    except ObjectDoesNotExist:
        raise ValidationError("Account ID provided does not exist.")
    return account


def validate_account_owner(user_id, account):
    customer = Customer.objects.get(user=user_id)
    user_accounts = Accounts.objects.filter(user=customer)
    if account not in user_accounts:
        raise ValidationError("Account provided does not belong to the user.")
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
        amount = json_dict["amount"].strip()
    except KeyError:
        raise ValidationError("Please input the amount.")

    try:
        amount = float(amount)
    except Exception:
        raise ValidationError("Amount provided is not a number.")
    rounded = round(amount, 2)
    if rounded != amount:
        raise ValidationError("Amount provided can only have a maximum of 2 decimal places.")
    if amount <= 0:
        raise ValidationError("Amount provided must be greater than 0.")
    return decimal.Decimal(str(amount))


def validate_description(json_dict):
    try:
        description = json_dict["description"].strip()
    except KeyError:
        raise ValidationError("Please input the description.")

    description = str(description)
    if len(description) > 255:
        raise ValidationError("Description provided cannot be longer than 255 characters")
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

def validate_not_too_much_amount(account, amount):
    if account.balance + amount > MAX_ACCOUNT_BALANCE:
        raise ValidationError("Total balance cannot exceed $9,999,999,999.99.")
    return True

def validate_account_not_closed(account):
    if account.status == Accounts.AccountStatus.CLOSED:
        raise ValidationError("Account provided is closed. No transactions can be done on this account.")
    return True

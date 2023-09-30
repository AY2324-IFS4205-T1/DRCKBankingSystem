from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from staff.models import Tickets
from staff.anonymise.overall import MAXIMUM_K_VALUE, QueryOptions

def validate_ticket_id(json_dict):
    try:
        ticket_id = json_dict["ticket_id"]
    except KeyError:
        raise ValidationError("Field 'ticket_id' missing.")

    try:
        ticket = Tickets.objects.get(ticket=ticket_id)
    except ObjectDoesNotExist:
        raise ValidationError("Ticket ID given does not exist.")
    return ticket

def validate_open_ticket(ticket):
    if ticket.status != Tickets.TicketStatus.OPEN:
        raise ValidationError("Ticket has already been closed.")
    return True


def validate_k_value(json_dict):
    try:
        k = int(json_dict["k_value"])
    except KeyError:
        raise ValidationError("Field 'k_value' missing.")
    except ValueError:
        raise ValidationError("K-value provided is not an integer")
    
    if k not in range(1, MAXIMUM_K_VALUE+1):
        raise ValidationError("K-value provided is not within the acceptable k-value range")
    
    return k

def validate_query(json_dict):
    try:
        query = json_dict["query"]
    except KeyError:
        raise ValidationError("Field 'query' missing.")

    if query not in [option.value for option in QueryOptions]:
        raise ValidationError("Value in 'query' field is not a recognised option")
    
    return query
        
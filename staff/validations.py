from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from staff.models import Tickets


def validate_ticket_id(json_dict):
    try:
        ticket_id = json_dict["ticket_id"].strip()
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

def validate_closed_ticket_owner(ticket, user):
    if ticket.closed_by in [user, None]:
        return True
    raise ValidationError("Closed ticket was not closed by the user.")
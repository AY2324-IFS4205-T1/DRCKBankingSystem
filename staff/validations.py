from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from staff.models import Tickets

def validate_ticket_id(ticket_id):
    try:
        ticket = Tickets.objects.get(ticket=ticket_id)
    except ObjectDoesNotExist:
        raise ValidationError("Ticket ID given does not exist.")
    return ticket

from datetime import datetime
from django.utils.timezone import make_aware
from rest_framework import serializers

from customer.models import AccountTypes, Accounts, Customer, Transactions
from .models import Staff, Tickets


class StaffSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Staff
        fields = ('user', 'first_name', 'last_name', 'title', 'birth_date', 'gender')

    def create(self, validated_data):
        return Staff.objects.create(**validated_data)


class GetAccountTypesSerializer(serializers.Serializer):
    
    def get_account_type_list(self):
        all_account_types = AccountTypes.objects.all().values_list("name", flat=True)
        return list(all_account_types)

      
class ApproveSerializer(serializers.Serializer):
    
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.ticket_id = json_dict["ticket_id"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        staff = Staff.objects.get(user=self.user_id)
        ticket = Tickets.objects.get(ticket=self.ticket_id)
        ticket.status = Tickets.TicketStatus.APPROVED
        ticket.closed_by = staff
        ticket.closed_date = make_aware(datetime.now())
        self.make_account(ticket)
        ticket.save()
        return ticket
    
    def make_account(self, ticket):
        account = Accounts.objects.create(user=ticket.created_by, type=ticket.account_type, status=Accounts.AccountStatus.ACTIVE)
        account.save()
        return account


class RejectSerializer(serializers.Serializer):
    
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.ticket_id = json_dict["ticket_id"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        staff = Staff.objects.get(user=self.user_id)
        ticket = Tickets.objects.get(ticket=self.ticket_id)
        ticket.status = Tickets.TicketStatus.REJECTED
        ticket.closed_by = staff
        ticket.closed_date = make_aware(datetime.now())
        ticket.save()
        return ticket


class GetOpenTicketsSerializer(serializers.Serializer):
    
    def get_open_tickets_list(self):
        self.all_open_tickets = Tickets.objects.filter(status=Tickets.TicketStatus.OPEN).order_by("created_date").values()
        return list(self.all_open_tickets)


class GetClosedTicketsSerializer(serializers.Serializer):
    
    def __init__(self, user_id):
        self.user_id = user_id

    def get_closed_tickets_list(self):
        staff = Staff.objects.get(user = self.user_id)
        closed_tickets = Tickets.objects.filter(closed_by=staff).exclude(status=Tickets.TicketStatus.OPEN).order_by("closed_date").reverse().values()
        return list(closed_tickets)

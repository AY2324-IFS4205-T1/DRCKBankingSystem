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


class ApproveSerializer(serializers.Serializer):
    
    def __init__(self, user_id, json_dict, **kwargs):
        self.staff = Staff.objects.get(user=user_id)
        self.ticket = json_dict["ticket_id"]
        self.ticket = Tickets.objects.get(ticket=self.ticket)
        super().__init__(**kwargs)

    def create(self, validated_data):
        self.ticket.status = Tickets.TicketStatus.APPROVED
        self.ticket.closed_by = self.staff
        self.ticket.closed_date = make_aware(datetime.now())
        self.ticket.save()
        self.make_account()
        return self.ticket
    
    def make_account(self):
        account = Accounts.objects.create(user=self.ticket.created_by, type=self.ticket.account_type, status=Accounts.AccountStatus.ACTIVE)
        account.save()
        return account


class RejectSerializer(serializers.Serializer):
    
    def __init__(self, user_id, json_dict, **kwargs):
        self.staff = Staff.objects.get(user=user_id)
        self.ticket = json_dict["ticket_id"]
        self.ticket = Tickets.objects.get(ticket=self.ticket)
        super().__init__(**kwargs)

    def create(self, validated_data):
        self.ticket.status = Tickets.TicketStatus.REJECTED
        self.ticket.closed_by = self.staff
        self.ticket.closed_date = make_aware(datetime.now())
        self.ticket.save()
        return self.ticket


class GetOpenTicketsSerializer(serializers.Serializer):
    
    def __init__(self):
        self.all_open_tickets = Tickets.objects.filter(status=Tickets.TicketStatus.OPEN).order_by("created_date").values()

    def get_open_tickets_list(self):
        return list(self.all_open_tickets)


class GetClosedTicketsSerializer(serializers.Serializer):
    
    def __init__(self, user_id):
        self.user_id = Staff.objects.get(user = user_id)
        self.closed_tickets = Tickets.objects.filter(closed_by=self.user_id).exclude(status=Tickets.TicketStatus.OPEN).order_by("closed_date").reverse().values()

    def get_closed_tickets_list(self):
        return list(self.closed_tickets)


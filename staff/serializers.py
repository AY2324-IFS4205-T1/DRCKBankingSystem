import json

from django.core.serializers import serialize
from django.utils import timezone
from rest_framework import serializers

from customer.models import Accounts, AccountTypes
from staff.validations import validate_open_ticket, validate_ticket_id

from .models import Staff, Tickets, RequestOpenAccount, RequestCloseAccount


class StaffSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Staff
        fields = ("user", "first_name", "last_name", "title", "birth_date", "gender")

    def create(self, validated_data):
        return Staff.objects.create(**validated_data)


class GetAccountTypesSerializer(serializers.Serializer):
    def get_account_type_list(self):
        all_account_types = AccountTypes.objects.all().values_list("name", flat=True)
        return list(all_account_types)


class ApproveSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, ticket_id, **kwargs):
        print(user_id)
        print(json_dict)
        self.user_id = user_id
        self.json_dict = json_dict
        self.json_dict['ticket_id'] = ticket_id
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.ticket = validate_ticket_id(self.json_dict)
        assert validate_open_ticket(self.ticket)
        return super().validate(attrs)

    def create(self, validated_data):
        staff = Staff.objects.get(user=self.user_id)
        self.ticket.status = Tickets.TicketStatus.APPROVED
        self.ticket.closed_by = staff
        self.ticket.closed_date = timezone.now()
        if self.ticket.ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
            self.create_account()
        elif self.ticket.ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
            self.close_account()
        self.ticket.save()
        return self.ticket

    def create_account(self):
        open_account_request = RequestOpenAccount.objects.get(ticket=self.ticket)

        account = Accounts.objects.create(
            user=self.ticket.created_by,
            type=open_account_request.account_type,
            status=Accounts.AccountStatus.ACTIVE,
        )
        account.save()
        return account
    
    def close_account(self):
        close_account_request = RequestCloseAccount.objects.get(ticket=self.ticket)
        print(close_account_request)
        print(close_account_request.account_id)

        close_account_request.account_id.status = Accounts.AccountStatus.CLOSED
        # account = Accounts.objects.get(account=close_account_request.account_id)
        # account.status = Accounts.AccountStatus.CLOSED
        close_account_request.account_id.save()
        return close_account_request.account_id

class RejectSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.ticket = validate_ticket_id(self.json_dict)
        assert validate_open_ticket(self.ticket)
        return super().validate(attrs)

    def create(self, validated_data):
        staff = Staff.objects.get(user=self.user_id)
        self.ticket.status = Tickets.TicketStatus.REJECTED
        self.ticket.closed_by = staff
        self.ticket.closed_date = timezone.now()
        self.ticket.save()
        return self.ticket


class GetOpenTicketsSerializer(serializers.Serializer):
    def get_open_tickets_list(self):
        self.all_open_tickets = (
            Tickets.objects.filter(status=Tickets.TicketStatus.OPEN)
            .order_by("created_date")
            .values()
        )
        return list(self.all_open_tickets)


class GetClosedTicketsSerializer(serializers.Serializer):
    def __init__(self, user_id):
        self.user_id = user_id

    def get_closed_tickets_list(self):
        staff = Staff.objects.get(user=self.user_id)
        closed_tickets = (
            Tickets.objects.filter(closed_by=staff)
            .exclude(status=Tickets.TicketStatus.OPEN)
            .order_by("closed_date")
            .reverse()
            .values()
        )
        return list(closed_tickets)


class TicketDetailsSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.ticket = validate_ticket_id(self.json_dict)
        return super().validate(attrs)

    def get_ticket_details(self):
        customer = self.ticket.created_by
        accounts = Accounts.objects.filter(user=customer).values()
        
        ticket_json = serialize("json", [self.ticket,])
        ticket_json = json.loads(ticket_json)[0]["fields"]
        customer_json = serialize("json", [customer,])
        customer_json = json.loads(customer_json)[0]["fields"]

        result = {
            "ticket": ticket_json,
            "customer": customer_json,
            "accounts": list(accounts),
        }
        return result

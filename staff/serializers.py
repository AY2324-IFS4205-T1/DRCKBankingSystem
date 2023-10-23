import json

from django.contrib.auth.password_validation import validate_password
from django.core.serializers import serialize
from django.utils import timezone
from rest_framework import serializers

from customer.models import Accounts, AccountTypes
from customer.validations import validate_name_length
from staff.validations import validate_closed_ticket_owner, validate_open_ticket, validate_ticket_id

from .models import RequestCloseAccount, RequestOpenAccount, Staff, Tickets



class StaffSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Staff
        fields = ("user", "first_name", "last_name", "title", "birth_date", "gender")
    
    def __init__(self, instance=None, data=..., user=user, **kwargs):
        self.user = user
        super().__init__(instance, data, **kwargs)

    def validate(self, attrs):
        assert validate_name_length(self.initial_data["first_name"])
        assert validate_name_length(self.initial_data["last_name"])
        validate_password(self.initial_data["password"], user=self.user)
        return super().validate(attrs)

    def create(self, validated_data):
        return Staff.objects.create(**validated_data)


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
        assert validate_closed_ticket_owner(self.ticket, self.user_id)
        return super().validate(attrs)

    def get_ticket_details(self):
        ticket_json = self.get_ticket_values()
        customer_json = self.get_customer_details()
        accounts = self.get_customer_accounts()

        result = {
            "ticket": ticket_json,
            "customer": customer_json,
            "accounts": accounts,
        }
        return result
    
    def get_ticket_values(self):
        ticket_json = serialize("json", [self.ticket,])
        ticket_json = json.loads(ticket_json)[0]["fields"]
        del ticket_json['created_by']
        del ticket_json['closed_by']
        ticket_json["value"] = None
        if self.ticket.ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
            ticket_json["value"] = RequestOpenAccount.objects.get(ticket=self.ticket).account_type.name
        if self.ticket.ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
            ticket_json["value"] = RequestCloseAccount.objects.get(ticket=self.ticket).account_id.account
        return ticket_json
    
    def get_customer_details(self):
        self.customer = self.ticket.created_by
        customer_json = serialize("json", [self.customer,])
        customer_json = json.loads(customer_json)[0]["fields"]
        del customer_json['address']
        del customer_json['postal_code']
        del customer_json['identity_no']
        del customer_json["gender"]
        customer_json["email"] = self.customer.user.email
        customer_json["phone_no"] = self.customer.user.phone_no
        return customer_json
    
    def get_customer_accounts(self):
        accounts = Accounts.objects.filter(user=self.customer)
        accounts_json = serialize("json", accounts)
        accounts_json = json.loads(accounts_json)
        accounts_list = list(account["fields"] for account in accounts_json)
        for account in accounts_list:
            del account["user"]
            account["type"] = AccountTypes.objects.get(type=account["type"]).name
        return accounts_list


class ApproveSerializer(serializers.Serializer):
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
        self.ticket.status = Tickets.TicketStatus.APPROVED
        self.ticket.closed_by = staff
        self.ticket.closed_date = timezone.now()
        if self.ticket.ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
            self.create_account()
        if self.ticket.ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
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
        close_account_request.account_id.status = Accounts.AccountStatus.CLOSED
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


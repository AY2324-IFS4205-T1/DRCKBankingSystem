from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework import serializers

from customer.validations import (validate_account, validate_account_owner,
                                  validate_account_type, validate_amount,
                                  validate_description,
                                  validate_no_repeated_ticket,
                                  validate_nric_and_citizenship,
                                  validate_sender_recipient,
                                  validate_sufficient_amount,
                                  validate_ticket_input,
                                  validate_total_balance)
from staff.models import RequestCloseAccount, RequestOpenAccount, Tickets

from .models import Customer, Transactions


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Customer
        fields = (
            "user",
            "first_name",
            "last_name",
            "birth_date",
            "identity_no",
            "address",
            "postal_code",
            "citizenship",
            "gender",
        )

    def __init__(self, instance=None, data=..., user=user, **kwargs):
        self.user = user
        super().__init__(instance, data, **kwargs)

    def validate(self, attrs):
        validate_password(self.initial_data["password"], user=self.user)
        validate_nric_and_citizenship(
            self.initial_data["identity_no"],
            self.initial_data["citizenship"],
            self.initial_data["birth_date"],
        )
        return super().validate(attrs)

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)


class GetTicketsSerializer(serializers.Serializer):
    def __init__(self, user_id):
        self.user_id = user_id

    def get_customer_tickets(self):
        user_id = Customer.objects.get(user=self.user_id)
        tickets = Tickets.objects.filter(created_by=user_id).values(
            "ticket", "ticket_type", "status", "created_date", "closed_date"
        )
        return list(tickets)


class CreateTicketSerializer(serializers.Serializer):
    def __init__(self, user, json_dict, **kwargs):
        self.user = user
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.customer = Customer.objects.get(user=self.user)
        self.ticket_type, self.value = validate_ticket_input(self.json_dict)
        if self.ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
            self.value = validate_account_type(self.value)
        if self.ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
            self.value = validate_account(self.json_dict, id_type="value")
            assert validate_account_owner(self.user, self.value)
        assert validate_no_repeated_ticket(
            self.customer, self.ticket_type, self.value
        )
        return super().validate(attrs)

    def create(self, validated_data):
        ticket = Tickets.objects.create(
            created_by=self.customer,
            status=Tickets.TicketStatus.OPEN,
            ticket_type=self.ticket_type,
        )
        if self.ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
            RequestOpenAccount.objects.create(
                ticket=ticket, account_type=self.value
            )
        if self.ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
            RequestCloseAccount.objects.create(
                ticket=ticket, account_id=self.value
            )
        return ticket


class TransactionsSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.customer_account = validate_account(self.json_dict)
        assert validate_account_owner(self.user_id, self.customer_account)
        return super().validate(attrs)

    def get_transactions(self):
        transactions = Transactions.objects.filter(
            Q(sender_id=self.customer_account) | Q(recipient_id=self.customer_account)
        ).values()
        return list(transactions)


class DepositSerializer(serializers.Serializer):

    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.customer_account = validate_account(self.json_dict)
        assert validate_account_owner(self.user_id, self.customer_account)
        self.amount = validate_amount(self.json_dict)
        return super().validate(attrs)

    def create(self, validated_data):
        Transactions.objects.create(
            recipient=self.customer_account,
            description="ATM Deposit",
            amount=self.amount,
            transaction_type=Transactions.TransactionTypes.DEPOSIT,
        )
        self.customer_account.balance = self.customer_account.balance + self.amount
        self.customer_account.save()
        return self.customer_account.balance


class WithdrawSerializer(serializers.Serializer):

    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.customer_account = validate_account(self.json_dict)
        assert validate_account_owner(self.user_id, self.customer_account)
        self.amount = validate_amount(self.json_dict)
        assert validate_sufficient_amount(self.customer_account, self.amount)
        return super().validate(attrs)

    def create(self, validated_data):
        Transactions.objects.create(
            sender=self.customer_account,
            description="ATM Withdrawal",
            amount=self.amount,
            transaction_type=Transactions.TransactionTypes.WITHDRAWAL,
        )
        self.customer_account.balance = self.customer_account.balance - self.amount
        self.customer_account.save()
        return self.customer_account.balance


class TransferSerializer(serializers.Serializer):

    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)

    def validate(self, attrs):
        self.sender_account = validate_account(self.json_dict, "sender_id")
        assert validate_account_owner(self.user_id, self.sender_account)
        self.recipient_account = validate_account(self.json_dict, "recipient_id")
        assert validate_sender_recipient(self.sender_account, self.recipient_account)
        self.initial_total = float(self.sender_account.balance) + float(
            self.recipient_account.balance
        )
        self.amount = validate_amount(self.json_dict)
        assert validate_sufficient_amount(self.sender_account, self.amount)
        self.description = validate_description(self.json_dict)
        return super().validate(attrs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(
            sender=self.sender_account,
            recipient=self.recipient_account,
            description=self.description,
            amount=self.amount,
            transaction_type=Transactions.TransactionTypes.TRANSFER,
        )
        self.sender_account.balance = float(self.sender_account.balance) - float(self.amount)
        self.recipient_account.balance = float(self.recipient_account.balance) + float(self.amount)
        assert validate_total_balance(self.initial_total, self.sender_account.balance, self.recipient_account.balance)
        self.sender_account.save()
        self.recipient_account.save()
        return ticket

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from customer.validations import (validate_account, validate_account_owner,
                                  validate_account_type, validate_amount,
                                  validate_description,
                                  validate_no_repeated_application,
                                  validate_nric_and_citizenship,
                                  validate_sender_recipient,
                                  validate_sufficient_amount,
                                  validate_total_balance)
from staff.models import Tickets, RequestCloseAccount, RequestOpenAccount

from .models import Accounts, AccountTypes, Customer, Transactions

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Customer
        fields = ('user', 'first_name', 'last_name', 'birth_date', 'identity_no', 'address', 'postal_code', 'citizenship', 'gender')
    
    def __init__(self, instance=None, data=..., user=user, **kwargs):
        self.user = user
        super().__init__(instance, data, **kwargs)

    def validate(self, attrs):
        validate_password(self.initial_data["password"], user=self.user)
        validate_nric_and_citizenship(self.initial_data["identity_no"], self.initial_data["citizenship"], self.initial_data["birth_date"])
        return super().validate(attrs)

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)
    
class CreateTicketSerializer(serializers.Serializer):
    ticket_type = serializers.CharField()
    value = serializers.CharField()
    
    def __init__(self, user, json_dict, **kwargs):
        self.user = user
        self.json_dict = json_dict
        super().__init__(**kwargs)
    
    # def validate(self, attrs):
    #     self.account_type = validate_account_type(self.json_dict)
    #     self.customer = Customer.objects.get(user=self.user_id)
    #     validate_no_repeated_application(self.customer, self.account_type)
    #     return super().validate(attrs)

    def create(self, validated_data):
        ticket_type = validated_data['ticket_type']
        value = validated_data['value']
        customer = Customer.objects.get(user=self.user)

        if ticket_type == Tickets.TicketType.OPEN_ACCOUNT:
            account_type = AccountTypes.objects.get(type=value)
            ticket = Tickets.objects.create(created_by=customer, status=Tickets.TicketStatus.OPEN, ticket_type=ticket_type)
            RequestOpenAccount.objects.create(ticket=ticket, account_type=account_type)
            return ticket
        elif ticket_type == Tickets.TicketType.CLOSE_ACCOUNT:
            closing_account = Accounts.objects.get(user=customer, account=value)
            ticket = Tickets.objects.create(created_by=customer, status=Tickets.TicketStatus.OPEN, ticket_type=ticket_type)
            RequestCloseAccount.objects.create(ticket=ticket, account_id=closing_account)
            return ticket
        else:
            raise TypeError()

class GetTicketsSerializer(serializers.Serializer):
    
    def __init__(self, user_id):
        self.user_id = user_id

    def get_customer_tickets(self):
        user_id = Customer.objects.get(user = self.user_id)
        tickets = Tickets.objects.filter(created_by=user_id).values("ticket", "ticket_type", "status", "created_date", "closed_date")
        return list(tickets)


class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = '__all__'
    # def __init__(self, user_id):
    #     self.user_id = user_id

    # def get_balance(self):
    #     user_id = Customer.objects.get(user = self.user_id)
    #     accounts = Accounts.objects.filter(user=user_id, status=Accounts.AccountStatus.ACTIVE).values("account", "type_id__name", "balance")
    #     return list(accounts)
    
    # def to_representation(self, instance):
    #     rep = super(GetBalanceSerializer, self).to_representation(instance)
    #     rep["type_id"] = instance.type_id.name
    #     del rep["type_id"]
    #     return rep

class DepositSerializer(serializers.Serializer):
    new_balance = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)

    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.customer_account = validate_account(self.json_dict)
        assert validate_account_owner(self.user_id, self.customer_account)
        self.amount = validate_amount(self.json_dict)
        self.description = validate_description(self.json_dict)
        return super().validate(attrs)

    def create(self, validated_data):
        Transactions.objects.create(recipient=self.customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.DEPOSIT)
        self.customer_account.balance = float(self.customer_account.balance) + float(self.amount)
        self.customer_account.save()
        validated_data['new_balance'] = self.customer_account.balance

        return validated_data


class WithdrawSerializer(serializers.Serializer):
    new_balance = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)

    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.customer_account = validate_account(self.json_dict)
        assert validate_account_owner(self.user_id, self.customer_account)
        self.amount = validate_amount(self.json_dict)
        assert validate_sufficient_amount(self.customer_account, self.amount)
        self.description = validate_description(self.json_dict)
        return super().validate(attrs)

    def create(self, validated_data):
        Transactions.objects.create(sender=self.customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.WITHDRAWAL)
        self.customer_account.balance = self.customer_account.balance - self.amount
        self.customer_account.save()
        validated_data['new_balance'] = self.customer_account.balance

        return validated_data


class TransferSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(required=False)

    class Meta:
        model = Transactions
        fields = '__all__'
    
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.json_dict = json_dict
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.sender_account = validate_account(self.json_dict, "sender_id")
        assert validate_account_owner(self.user_id, self.sender_account)
        self.recipient_account = validate_account(self.json_dict, "recipient_id")
        assert validate_sender_recipient(self.sender_account, self.recipient_account)
        self.initial_total = float(self.sender_account.balance) + float(self.recipient_account.balance)
        self.amount = validate_amount(self.json_dict)
        assert validate_sufficient_amount(self.sender_account, self.amount)
        self.description = validate_description(self.json_dict)
        return super().validate(attrs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(sender=self.sender_account, recipient=self.recipient_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.TRANSFER)
        self.sender_account.balance = float(self.sender_account.balance) - float(self.amount)
        self.recipient_account.balance = float(self.recipient_account.balance) + float(self.amount)
        assert validate_total_balance(self.initial_total, self.sender_account.balance, self.recipient_account.balance)
        self.sender_account.save()
        self.recipient_account.save()
        
        return ticket

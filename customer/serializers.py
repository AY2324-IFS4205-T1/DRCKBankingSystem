from rest_framework import serializers

from customer.validations import validate_account, validate_account_owner, validate_account_type, validate_amount, validate_description, validate_sender_recipient, validate_sufficient_amount, validate_total_balance
from staff.models import Tickets

from .models import Accounts, AccountTypes, Customer, Transactions


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Customer
        fields = ('user', 'first_name', 'last_name', 'birth_date', 'identity_no', 'address', 'nationality', 'gender')

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)
    

class GetAccountTypesSerializer(serializers.Serializer):
    
    def __init__(self, user_id):
        self.all_account_types = AccountTypes.objects.values_list("name", flat=True)

    def get_account_type_list(self):
        return list(self.all_account_types)
    

class ApplySerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.account_type = json_dict["account_type"]
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.account_type_model = validate_account_type(self.account_type)
        return super().validate(attrs)

    def create(self, validated_data):
        customer = Customer.objects.get(user=self.user_id)
        ticket = Tickets.objects.create(created_by=customer, account_type=self.account_type_model, status = Tickets.TicketStatus.OPEN)
        return ticket


class GetBalanceSerializer(serializers.Serializer):
    
    def __init__(self, user_id):
        self.user_id = user_id

    def get_balance(self):
        user_id = Customer.objects.get(user = self.user_id)
        accounts = Accounts.objects.filter(user=user_id, status=Accounts.AccountStatus.ACTIVE).values("account", "type_id", "balance")
        return list(accounts)


class DepositSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.account_id = json_dict["account_id"]
        self.amount = json_dict["amount"]
        self.description = json_dict["description"]
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.customer_account = validate_account(self.account_id)
        assert validate_account_owner(self.user_id, self.customer_account)
        self.amount = validate_amount(self.amount)
        self.description = validate_description(self.description)
        return super().validate(attrs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(recipient=self.customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.DEPOSIT)
        self.customer_account.balance = self.customer_account.balance + self.amount
        self.customer_account.save()
        return ticket


class WithdrawSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.account_id = json_dict["account_id"]
        self.amount = json_dict["amount"]
        self.description = json_dict["description"]
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.customer_account = validate_account(self.account_id)
        assert validate_account_owner(self.user_id, self.customer_account)
        self.amount = validate_amount(self.amount)
        assert validate_sufficient_amount(self.customer_account, self.amount)
        self.description = validate_description(self.description)
        return super().validate(attrs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(sender=self.customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.WITHDRAWAL)
        self.customer_account.balance = self.customer_account.balance - self.amount
        self.customer_account.save()
        return ticket


class TransferSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.sender_id = json_dict["sender_id"]
        self.amount = json_dict["amount"]
        self.description = json_dict["description"]
        self.recipient_id = json_dict["recipient_id"]
        super().__init__(**kwargs)
    
    def validate(self, attrs):
        self.sender_account = validate_account(self.sender_id)
        assert validate_account_owner(self.user_id, self.sender_account)
        self.recipient_account = validate_account(self.recipient_id)
        assert validate_sender_recipient(self.sender_account, self.recipient_account)
        self.initial_total = self.sender_account.balance + self.recipient_account.balance
        self.amount = validate_amount(self.amount)
        assert validate_sufficient_amount(self.sender_account, self.amount)
        self.description = validate_description(self.description)
        return super().validate(attrs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(sender=self.sender_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.TRANSFER)
        self.sender_account.balance = self.sender_account.balance - self.amount
        self.recipient_account.balance = self.recipient_account.balance + self.amount
        assert validate_total_balance(self.initial_total, self.sender_account.balance, self.recipient_account.balance):
        self.sender_account.save()
        self.recipient_account.save()
        return ticket

from rest_framework import serializers

from staff.models import Tickets
from .models import AccountTypes, Accounts, Customer, Transactions


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

    def create(self, validated_data):
        customer = Customer.objects.get(user=self.user_id)
        account_type = AccountTypes.objects.get(name=self.account_type)
        ticket = Tickets.objects.create(created_by=customer, account_type=account_type, status = Tickets.TicketStatus.OPEN)
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
        self.amount = json_dict["amount"]
        self.description = json_dict["description"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        customer = Customer.objects.get(user=self.user_id)
        customer_account = Accounts.objects.get(user=customer)
        ticket = Transactions.objects.create(recipient=customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.DEPOSIT)
        customer_account.balance = customer_account.balance + self.amount
        customer_account.save()
        return ticket


class WithdrawSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.amount = json_dict["amount"]
        self.description = json_dict["description"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        customer = Customer.objects.get(user=self.user_id)
        customer_account = Accounts.objects.get(user=customer)
        ticket = Transactions.objects.create(sender=customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.WITHDRAWAL)
        customer_account.balance = customer_account.balance - self.amount
        customer_account.save()
        return ticket


class TransferSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.user_id = user_id
        self.amount = json_dict["amount"]
        self.description = json_dict["description"]
        self.recipient_account = json_dict["recipient_id"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        customer = Customer.objects.get(user=self.user_id)
        customer_account = Accounts.objects.get(user=customer)
        recipient_account = Accounts.objects.get(account=self.recipient_account)
        ticket = Transactions.objects.create(sender=customer_account, description=self.description, amount=self.amount, transaction_type=Transactions.TransactionTypes.TRANSFER)
        customer_account.balance = customer_account.balance - self.amount
        recipient_account.balance = recipient_account.balance + self.amount
        customer_account.save()
        recipient_account.save()
        return ticket

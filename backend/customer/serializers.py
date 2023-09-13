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
        self.customer = Customer.objects.get(user=user_id)
        self.account_type = json_dict["account_type"]
        self.account_type = AccountTypes.objects.get(name=self.account_type)
        super().__init__(**kwargs)

    def create(self, validated_data):
        ticket = Tickets.objects.create(created_by=self.customer, account_type=self.account_type, status = Tickets.TicketStatus.OPEN)
        return ticket


class GetBalanceSerializer(serializers.Serializer):
    
    def __init__(self, user_id):
        self.user_id = Customer.objects.get(user = user_id)
        self.accounts = Accounts.objects.filter(user=self.user_id, status=Accounts.AccountStatus.ACTIVE).values("account", "type_id", "balance")

    def get_balance(self):
        return list(self.accounts)


class DepositSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.customer = Customer.objects.get(user=user_id)
        self.customer_account = Accounts.objects.get(user=self.customer)
        self.amount = json_dict["amount"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(recipient=self.customer_account, description="Deposit", amount=self.amount)
        self.customer_account.balance = self.customer_account.balance + self.amount
        self.customer_account.save()
        return ticket


class WithdrawSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.customer = Customer.objects.get(user=user_id)
        self.customer_account = Accounts.objects.get(user=self.customer)
        self.amount = json_dict["amount"]
        super().__init__(**kwargs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(sender=self.customer_account, description="Withdrawal", amount=self.amount)
        self.customer_account.balance = self.customer_account.balance - self.amount
        self.customer_account.save()
        return ticket


class TransferSerializer(serializers.Serializer):
    def __init__(self, user_id, json_dict, **kwargs):
        self.customer = Customer.objects.get(user=user_id)
        self.customer_account = Accounts.objects.get(user=self.customer)
        self.amount = json_dict["amount"]
        self.recipient_account = json_dict["recipient_id"]
        self.recipient_account = Accounts.objects.get(account=self.recipient_account)
        super().__init__(**kwargs)

    def create(self, validated_data):
        ticket = Transactions.objects.create(sender=self.customer_account, description="Transfer", amount=self.amount)
        self.customer_account.balance = self.customer_account.balance - self.amount
        self.recipient_account.balance = self.recipient_account.balance + self.amount
        self.customer_account.save()
        self.recipient_account.save()
        return ticket


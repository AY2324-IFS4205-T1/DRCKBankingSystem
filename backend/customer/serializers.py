from rest_framework import serializers

from staff.models import Tickets
from .models import AccountTypes, Customer

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


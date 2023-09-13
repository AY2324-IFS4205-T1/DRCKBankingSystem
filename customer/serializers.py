from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Customer
        fields = ('user', 'first_name', 'last_name', 'birth_date', 'identity_no', 'address', 'nationality', 'gender')

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)
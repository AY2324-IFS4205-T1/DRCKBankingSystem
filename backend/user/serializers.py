from rest_framework import serializers
from .models import User
# from customer.models import Customer
from customer.serializers import CustomerSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_no', 'type', 'password')

    def create(self, validated_data):
        foo = None
        customer_serializer = CustomerSerializer(data=self.initial_data)
        if customer_serializer.is_valid():
            foo = User.objects.create_user(**validated_data)
            customer_serializer.save(user=foo)
        return foo
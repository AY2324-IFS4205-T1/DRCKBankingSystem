from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User
from customer.serializers import CustomerSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_no', 'password')

    def create(self, validated_data):
        new_user = None
        validate_password(validated_data['password'])

        customer_serializer = CustomerSerializer(data=self.initial_data)
        if customer_serializer.is_valid():
            new_user = User.objects.create_user(**validated_data, type=self.context['type'])
            customer_serializer.save(user=new_user)
        return new_user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    type = serializers.SerializerMethodField()

    def validate(self, data):
        username = data['username']
        password = data['password']
        type = self.context['type']

        user = authenticate(request=self.context.get('request'), username=username, password=password, type=type)

        if not user:
            raise serializers.ValidationError()
        
        data['user'] = user
        return data
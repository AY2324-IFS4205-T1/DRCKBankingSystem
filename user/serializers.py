from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.fields import empty

from user.validations import validate_new_user
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_no', 'password')
    
    def __init__(self, user_type, instance=None, data=..., **kwargs):
        self.user_type = user_type
        super().__init__(instance, data, **kwargs)

    def validate(self, attrs):
        username = attrs['username']
        validate_new_user(username, self.user_type)
        return super().validate(attrs)
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    user_type = serializers.SerializerMethodField()

    def __init__(self, user_type, instance=None, data=..., **kwargs):
        self.user_type = user_type
        super().__init__(instance, data, **kwargs)

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(request=self.context.get('request'), username=username, password=password, type=self.user_type)
        if not user:
            raise serializers.ValidationError()
        
        data['user'] = user
        return data

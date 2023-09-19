from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_no', 'password')

    def create(self, validated_data):        
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    user_type = serializers.SerializerMethodField()

    def validate(self, data):
        username = data['username']
        password = data['password']
        user_type = self.context['type']
        user = authenticate(request=self.context.get('request'), username=username, password=password, type=user_type)

        if not user:
            raise serializers.ValidationError()
        
        data['user'] = user
        return data

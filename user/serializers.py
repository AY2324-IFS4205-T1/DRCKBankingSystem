from secrets import choice
from string import ascii_letters

from django.contrib.auth import authenticate
from rest_framework import serializers

from user.twofa import generate_qr, verify_otp
from user.validations import validate_new_user, validate_otp, validate_user_2fa

from .models import TwoFA, User


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


class GetTwoFASerializer(serializers.Serializer):
    def __init__(self, user, **kwargs):
        self.user = user
        super().__init__(**kwargs)
    
    def get_qr_code(self):
        twofa = TwoFA.objects.get_or_create(user=self.user)[0]
        twofa.key = ''.join(choice(ascii_letters) for _ in range(1024))
        twofa.save()
        return generate_qr(twofa.key, self.user.username)


class VerifyTwoFASerializer(serializers.Serializer):
    def __init__(self, user, json_dict, **kwargs):
        self.user = user
        self.json_dict = json_dict
        super().__init__(**kwargs)
        
    def validate(self, attrs):
        self.otp = validate_otp(self.json_dict)
        self.two_fa = validate_user_2fa(self.user)
        return super().validate(attrs)

    def verify(self):
        return verify_otp(self.two_fa.key, self.otp)


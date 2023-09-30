from django.contrib.auth import authenticate
from django.utils import timezone
from pyotp import random_base32
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
        two_fa = TwoFA.objects.get_or_create(user=self.user)[0]
        two_fa.key = random_base32()
        two_fa.save()
        return generate_qr(two_fa.key, self.user.username)


class VerifyTwoFASerializer(serializers.Serializer):
    def __init__(self, user, json_dict, authorisation_header, **kwargs):
        self.user = user
        self.json_dict = json_dict
        self.authorisation_header = ""
        if authorisation_header[:6] == "Token ":
            self.authorisation_header = authorisation_header[6:]
        super().__init__(**kwargs)
        
    def validate(self, attrs):
        self.otp = validate_otp(self.json_dict)
        self.two_fa = validate_user_2fa(self.user)
        return super().validate(attrs)

    def verify(self):
        result = verify_otp(self.two_fa.key, self.otp)
        if result:
            self.two_fa.last_authenticated = timezone.now()
            self.two_fa.knox_token = self.authorisation_header
        else:
            self.two_fa.last_authenticated = None
            self.two_fa.knox_token = ""
        self.two_fa.save()
        return {"2FA success": result, "last_authenticated": self.two_fa.last_authenticated}


class RemoveTwoFASerializer(serializers.Serializer):
    def __init__(self, user, **kwargs):
        self.user = user
        two_fa = TwoFA.objects.get(user=self.user)
        two_fa.last_authenticated = None
        two_fa.knox_token = ""
        two_fa.save()
        super().__init__(**kwargs)


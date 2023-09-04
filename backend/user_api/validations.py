from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class Validations():

    def custom_validation(self, data):
        email = data['email'].strip()
        username = data['username'].strip()
        password = data['password'].strip()
        ##
        if not email or UserModel.objects.filter(email=email).exists():
            raise ValidationError('choose another email')
        ##
        if not password or len(password) < 8:
            raise ValidationError('choose another password, min 8 characters')
        ##
        if not username:
            raise ValidationError('choose another username')
        return data


    def validate_email(self, data):
        email = data['email'].strip()
        if not email:
            raise ValidationError('an email is needed')
        return True

    def validate_username(self, data):
        username = data['username'].strip()
        if not username:
            raise ValidationError('choose another username')
        return True

    def validate_password(self, data):
        password = data['password'].strip()
        if not password:
            raise ValidationError('a password is needed')
        return True
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

# https://reintech.io/blog/writing-custom-authentication-backend-django

class UserAuth:
    def authenticate(self, request, username=None, password=None, type=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username, type=type)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
            
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
            
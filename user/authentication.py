from django.contrib.auth import get_user_model

# https://reintech.io/blog/writing-custom-authentication-backend-django

class UserAuth:
    def authenticate(self, _, username=None, password=None, type=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username, type=type)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
            
    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
            
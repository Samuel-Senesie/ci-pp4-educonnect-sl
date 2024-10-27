from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Custom backend to authrnticate users using either email or phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.object.get(email_or_phone = username)
        except CustomUser.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

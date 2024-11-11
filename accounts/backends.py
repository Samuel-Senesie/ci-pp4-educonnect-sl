from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Custom backend to authrnticate users using either username, email or phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        try:
            # Check if identifier is email, phone, or username
            if '@' in username: #Email
                user = CustomUser.objects.get(email_or_phone=username)
            elif username.isdigit():  #Phone
                user = CustomUser.objects.get(email_or_phone=username)
            else: # Username
                user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return None
        
        # Authenticate using password if user is found
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
        
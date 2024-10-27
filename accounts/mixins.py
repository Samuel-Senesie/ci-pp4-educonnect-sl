from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

class PasswordValidationMixin:
    """
    A mixin for handling password validation in multiple forms.
    """
    def validate_password_strength(self, password):
        validate_password(password)
        return password
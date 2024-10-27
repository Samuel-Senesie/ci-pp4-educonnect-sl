from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser, UserProfile
from .mixins import PasswordValidationMixin
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm, PasswordValidationMixin):
    """
    Form for creating a new user with required fields
    """

    username = forms.CharField(
        required=False,
        label=_("Username"),
        help_text=_("Optional username for your account.")
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_("Date of Birth *"),
        help_text=_("Must be 18 or older."),
        required=True
    )

    preferred_time_from = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'timepicker'}),
        label=_("From")
    )

    preferred_time_to = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'timepicker'}),
        label=_("To")
    )

    preferred_means_of_communication = forms.ChoiceField(
        choices=[
            ('sms', 'SMS'),
            ('email', 'Email'),
            ('whatsapp', 'WhatsApp')
        ],
        widget=forms.RadioSelect(attrs={'class': 'icon-radio'}),
        label=_("Preferred Means of Communication")
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'id': 'id_password1'}),
        required=True,
        help_text=_("Your password must contain at least 8 characters, include letters and numbers."),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'id': 'id_password2'}),
        required=True,
        help_text=_("Repeat the same password as before, for verification."),
    )

    accept_terms = forms.BooleanField(
        label=_("I agree to the Terms and Conditions"),
        required=True,
        error_messages={'required': _("You must accept the terms and conditions to signup.")}
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'username', 'email_or_phone', 'date_of_birth', 'gender', 'user_role',
            'preferred_means_of_communication', 'preferred_time_from', 'preferred_time_to'
        )

    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match."))
        return password2
    
    #def generate_password(self, length=12):
        #characters = string.ascii_letters + string.digits + string.punctuation
        #return ''.join(random.choice(characters) for _ in range(length))

    
    def clean_date_of_birth(self):
        #  Validate that the user is 18 or above
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = timezone.now().date()
            age = (today - dob).days // 365
            if age < 18:
                raise ValidationError(_("You must be at least 18 years old to register."))
        return dob

class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating an existing user.
    """

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'email_or_phone', 'date_of_birth', 'gender',
            'user_role', 'preferred_means_of_communication', 
            'preferred_time_from', 'preferred_time_to', 'is_active', 'is_verified'
        )

class CustomLoginForm(AuthenticationForm):
    """
    Custom form for logging in using either email or phone.
    """
    identifier = forms.CharField(max_length=255, label=_("Username, Email or Phone"))
    password = forms.CharField(widget=forms.PasswordInput, label=_("Password"))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput, label=_("Remember Me"))

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('identifier')
        password = cleaned_data.get('password')

        if not identifier or not password:
            raise forms.ValidationError(_("Both identifier and password are required."))

        #  Check id indentifier is emial or phone
        user_model = get_user_model()

        try:
            if '@' in identifier:
                user = user_model.objects.get(email=identifier)
            else:
                user =user_model.objects.get(email=identifier)
        except user_model.DoesNotExist:
            raise forms.ValidationError(_("Invalid credentials. Please try again."))
        
        user = authenticate(self.request, username=user.username, password=password)

        if user is None:
            raise ValidationError(_("Invalid credentials. Please try again."))
        
        return cleaned_data
    

class UserProfileForm(forms.ModelForm):
    """
    Form for updating the user's profile information, such as bio and profile picture.
    """

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'location']
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture and picture.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError(_("Profile picture must be under 5MB."))
        return picture

class PasswordResetRequestForm(PasswordResetForm):
    """
    Form to request a password reset by providing email or phone.
    """
    email_or_phone = forms.CharField(max_length=255, label=_("Email or Phone"))

    def clean_email_or_phone(self):
        data = self.cleaned_data['email_or_phone']
        if not CustomUser.objects.filter(email_or_phone=data).exists():
            raise ValidationError(_("There is no account with that email or phone."))
        return data

class SetNewPasswordForm(SetPasswordForm, PasswordValidationMixin):
    """
    Form to set new password after password reset request.
    """
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput,
        help_text=_("Your password must contain at least 8 charachters, including leters, numbers, and special characters."),
        validators=[validate_password]
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput,
        help_text=_("Repeat the same password as before, for verification.")
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        return password2
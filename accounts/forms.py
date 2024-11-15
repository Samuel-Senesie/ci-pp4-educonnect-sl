from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser, UserProfile
from .mixins import PasswordValidationMixin
from django.utils import timezone
from django.core.validators import EmailValidator, RegexValidator
from PIL import Image, ImageFile
from django.core.files.base import ContentFile
from io import BytesIO



class CustomUserCreationForm(UserCreationForm, PasswordValidationMixin):
    """
    Form for creating a new user with required fields
    """
    username = forms.CharField(
        required=False,
        label=_("Username"),
        help_text=_("Optional username for your account."),
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'id': 'username'})
    )

    email_or_phone = forms.CharField(
        label="Email or Phone",
        max_length=255,
        widget=forms.TextInput(attrs={'autocomplete': 'email', 'id': 'email_or_phone'}),
        help_text="Enter a valid email or phone number."
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'autocomplete': 'bday', 'id': 'date_of_birth'}),
        label=_("Date of Birth"),
        help_text=_("Must be 18 or older."),
        required=True
    )

    preferred_time_from = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'timepicker', 'id': 'preferred_time_from'}),
        label=_("From"),
        required=False
    )

    preferred_time_to = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'timepicker', 'id': 'preferrerd_time_to'}),
        label=_("To"),
        required=False
    )

    preferred_means_of_communication = forms.ChoiceField(
        choices=[
            ('sms', 'SMS'),
            ('email', 'Email'),
            ('whatsapp', 'WhatsApp')
        ],
        widget=forms.RadioSelect, #(attrs={'class': 'icon-radio', 'id': 'preferred_means_of_communication'}),
        label=_("Preferred Means of Communication"),
        required=False
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'id': 'id_password1'}),
        required=True,
        help_text=_("Your password must contain at least 8 characters, include letters and numbers."),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'id': 'id_password2'}),
        required=True,
        help_text=_("Repeat the same password as before, for verification."),
    )

    accept_terms = forms.BooleanField(
        label=_("I agree to the Terms and Conditions"),
        required=True,
        error_messages={'required': _("You must accept the terms and conditions to signup.")},
        widget=forms.CheckboxInput(attrs={'id': 'accept_terms'})
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'username', 'email_or_phone', 'date_of_birth', 'gender', 'user_role',
            'preferred_means_of_communication', 'preferred_time_from', 'preferred_time_to', 'accept_terms'
        )
    
    def clean_email_or_phone(self):
        """Validate that the email_or_phone field accepts either valid email or phone number"""
        #data = self.cleaned_data['email_or_phone']
        email_or_phone = self.cleaned_data.get('email_or_phone')
        email_validator = EmailValidator(_('Enter a valid email address.'))
        phone_validator = RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')
        try:
            email_validator(email_or_phone)
        except ValidationError:
            try:
                phone_validator(email_or_phone)

            except ValidationError:
                raise ValidationError(_("Enter a valid email or phone number."))
        return email_or_phone
    

    def clean_date_of_birth(self):
        #  Validate that the user is 18 or above
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = timezone.now().date()
            age = (today - dob).days // 365
            if age < 18:
                raise ValidationError(_("You must be at least 18 years old to register."))
        return dob

    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match."))
        return password2
    
    #def generate_password(self, length=12):
        #characters = string.ascii_letters + string.digits + string.punctuation
        #return ''.join(random.choice(characters) for _ in range(length))

    
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'profile_picture']    

class CustomUserProfileEditForm(ProfileEditForm):
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
    identifier = forms.CharField(
        max_length=255, 
        label="Username, Email, or Phone", 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Username, Email or Phone',
            'autocomplete': 'username', 
            #'id': 'id_identifier'
        }),
        #help_text="Enter your username, email or phone number."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
            #'id': 'id_password',
            'placeholder': 'Password'
        }), 
        #label=_("Password")
    )
    username = forms.CharField(
        widget=forms.HiddenInput(),
	    required=False
    )

    remember_me = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'id': 'id_remember_me'}), 
        label=_("Remember Me"))

    def clean(self):
        identifier = self.cleaned_data.get('identifier')
        password = self.cleaned_data.get('password')

        print(f"identifier recieved: {identifier}")
        print(f"password recieved: {password}")

        #if not identifier or not password:
        #    raise forms.ValidationError(_("Both identifier and password are required."))
        
        user_model = get_user_model()
        user = None

        try:

            if '@' in identifier:  # Assume email if '@' is present
                user = user_model.objects.get(email_or_phone=identifier)

            elif identifier.isdigit():  # Assume phone number if all digits 
                user =user_model.objects.get(email_or_phone=identifier)
            else:
                user = user_model.objects.get(username=identifier)
            print(f"User found with identifier {identifier}")

            if user.username:
                self.cleaned_data['username'] = user.username
            else:
                self.cleaned_data['username'] = user.email_or_phone
        except user_model.DoesNotExist:
            print("User does not exist with the given identifier")
            raise forms.ValidationError(_("Invalid login credentials. Please try again."))
        
        # Authenticate the found user with the password
        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is None:
            print(f"Authentiction failed for user {user.username} with password {password}")
            raise forms.ValidationError(_("Invalid login credentials. Please try again"))
        
        else:
            print(f"Authentication successful for user {user.username}")

        #if user is None:
        #    print(f"Authentication failed")
        #    raise forms.ValidationError(_("Invalid credentials. Please try again."))
        
        print(self.cleaned_data["username"])
        self.cleaned_data['user'] = authenticated_user
        return self.cleaned_data

        #user = authenticate(self.request, username=user.username, password=password)

        #if user is None:
        #    raise ValidationError(_("Invalid credentials. Please try again."))

ImageFile.LOAD_TRUNCATED_IMAGES = True

def validate_and_resize_image(image_file, max_size=5 * 102 *1024, max_dimensions=(1024, 521)):
    
    if not image_file:
        raise ValidationError("No image file provided.")

    # Check file size
    if image_file.size > max_size:
        raise ValidationError(f"Image size should not excee {max_size / (1024 * 1024):.2f} MB.")
    
    # Open the image
    try:
        image = Image.open(image_file)
    except Exception as e:
        raise ValidationError("Invalid image file.") from e
    
    # Validate file format
    valid_formats = {"JPEG", "PNG", "GIF"}
    if image.format not in valid_formats:
        raise ValidationError("Unsupported file format. Allowed formats are: {', '.join(valid_formats)}.")
    
    # Convert to RGB if necessary
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB") # Convert to JPEG-compatible format if needed

    # Resize the image
    image.thumbnail(max_dimensions, Image.Resampling.LANCZOS)

    # Save resized image to a temporary buffer
    temp_image = BytesIO()
    image.save(temp_image, format='JPEG', quality=85)
    temp_image.seek(0)

    return ContentFile(temp_image.read(), name=image_file.name)

class UserProfileForm(forms.ModelForm):
    """
    Form for updating the user's profile information, such as bio and profile picture.
    """

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'background_image', 'location']
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            return validate_and_resize_image(profile_picture, max_dimensions=(300, 300))
        return profile_picture
    
    def cleaned_background_image(self):
        background_image = self.cleaned_data.get('background_image')
        if background_image:
            return validate_and_resize_image(background_image, max_dimensions=(1024, 512))
        return background_image
    
    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle profile picture replacement
        if 'profile_picture' in self.changed_data and instance.profile_picture:
            if instance.profile_picture.name != 'default_profile_pic.jpeg':
                instance.profile_picture.delete(save=False)
        
        # Handle background image replacement
        if 'background_image' in self.changed_data and instance.background_image:
            if instance.background_image.name != 'background_image.jpeg':
                instance.background_image.delete(save=False)
        
        if commit:
            instance.save()
        
        return instance

class PasswordResetRequestForm(PasswordResetForm):
    """
    Form to request a password reset by providing email or phone.
    """
    email_or_phone = forms.CharField(
        max_length=255, 
        label=_("Email or Phone"), 
        widget=forms.TextInput(attrs={'autocomplete': 'email', 'id': 'email_or_phone'})
    )


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
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'id': 'new_password1'}),
        help_text=_("Your password must contain at least 8 charachters, including leters, numbers, and special characters."),
        validators=[validate_password]
    )

    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'id': 'new_password2'}),
        help_text=_("Repeat the same password as before, for verification.")
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        return password2
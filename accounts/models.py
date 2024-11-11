from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import RegexValidator, EmailValidator

# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle creating regular users and superusers.
    """
    def create_user(self, email_or_phone, username=None, password=None, **extra_fields):
        if not email_or_phone:
            raise ValueError(_('Please enter a valid email or phone number to proceed.'))
        if not extra_fields.get('first_name'):
            raise ValueError(_('First name is required.'))
        if not extra_fields.get('last_name'):
            raise ValueError(_('Last name is required.'))

        #if not extra_fields.get('is_superuser') and 'date_of_birth' not in extra_fields:
            #raise ValueError(_('Date of birth is required.'))
        #if not extra_fields.get('is_superuser'):
            #date_of_birth = extra_fields.get('date_of_birth')
            #if date_of_birth is None:
            #    raise ValueError(_("Date of birth is required for all regular users."))
        #else:
            #extra_fields.pop('date_of_birth', None)
        
        #  Ensure date of birth is provided by regular users but not for superuser
        date_of_birth = extra_fields.pop('date_of_birth', None)
        if not extra_fields.get('is_superuser') and date_of_birth is None:
            raise ValueError(_("Date of birth is required for all regular users."))

        email_or_phone = self.normalize_email(email_or_phone)
        extra_fields.setdefault('is_active', True)
        #user = self.model(email_or_phone=email_or_phone, date_of_birth=date_of_birth, **extra_fields)
        user = self.model(email_or_phone=email_or_phone, date_of_birth=date_of_birth, username=username, **extra_fields)
        user.set_password(password) #  Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email_or_phone, password, **extra_fields):
        """
        Create and return Superuser.Superuser requires an email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        #extra_fields.setdefault('date_of_birth', None)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        if not username:
            raise ValueError('Superuser must have a username')
        if not password:
            raise ValueError('Superuser must have a password.')
        
        if not extra_fields.get('first_name'):
            raise ValueError('Superuser must have a first name.')
        if not extra_fields.get('last_name'):
            raise ValueError('Superuser must have a first name.')
        
        # Make date of birth not required for superuser
        extra_fields.pop('date_of_birth', None)  
        # = extra_field.get('date_of_birth',None)
    
        return self.create_user(email_or_phone=email_or_phone, username=username, password=password, **extra_fields)
    
    def get_by_natural_key(self, email_or_phone):
        return self.get(email_or_phone=email_or_phone)
    


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for handling both regular users and superusers.
    """

    USER_ROLES = [
        ('Parent', 'Parent'),
        ('Teacher', 'Teacher'),
        ('Administrator', 'Administrator'),
        ('Police', 'Police'),
        ('MCA', 'MCA')
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    COMMUNICATION_PREFERENCE = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ]


    username = models.CharField(_('username'), max_length=255, null=True, blank=True)
    user_role = models.CharField(_('user role'), max_length=50, choices=USER_ROLES)
    first_name = models.CharField(_('first name'), max_length=50)
    last_name = models.CharField(_('last name'), max_length=50)
    email_or_phone = models.CharField(
        _('email or phone'), 
        max_length=255, 
        unique=True, 
        #validators=[
            #EmailValidator(_('Enter a valid email address.'), code='invalid_email'), 
            #RegexValidator(r'^\+?1?\d{9,15}$', _('Enter a valid phone number.'), code='invalid_phone')
        #]
    )
    is_parent = models.BooleanField(default=False)
    is_school_staff = models.BooleanField(default=False)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True) # default='2000-01-01'
    gender = models.CharField(_('gender'), max_length=10, choices=GENDER_CHOICES)
    #location = models.ForeignKey('Location', no_delete=models.SET_NULL, null=True)
    preferred_means_of_communication = models.CharField(
        _('preferred means of communication'), 
        max_length=20, 
        choices=COMMUNICATION_PREFERENCE, 
        default='sms'
    )
    preferred_time_from = models.TimeField(_('preferred time from'), null=True, blank=True)
    preferred_time_to = models.TimeField(_('preferred time to'), null=True, blank=True)
    is_verified = models.BooleanField(_('is verified'), default=False)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Indicates if user account is active.'))
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_superuser = models.BooleanField(_('superuser status'), default=False, help_text=_('Designate that this user has all the permisions without explicity assigning them.'))
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email_or_phone'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    def get_short_name(self):
        return self.first_name.strip()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.user_role})'

#  UserProfile model
class UserProfile(models.Model):
    
    """
    Profile model that handle and store additional user information.
    """
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(_('bio'), max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(_('profile picture'), default='default.jpeg', upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(_('location'), max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.location or "Location not provided"} (UserProfile)'
    
   
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        ordering = ['user__last_name']

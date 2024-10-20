from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core import validators

# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle creating regular users and superusers.
    """
    def create_user(self, email_or_phone, password=None, **extra_fields):
        if not email_or_phone:
            raise ValueError(_('Please enter a valid email or phone number to proceed.'))
        if not extra_fields.get('first_name'):
            raise ValueError(_('First name is required.'))
        if not extra_fields.get('last_name'):
            raise ValueError(_('Last name is required.'))

        date_of_birth = extra_fields.pop('date_of_birth', None)
        if not date_of_birth:
            raise ValueError(_('The date of birth is required for regular users.'))
        
        email_or_phone = self.normalize_email(email_or_phone)
        user = self.model(email_or_phone=email_or_phone, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(password) #Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and return Superuser.
        Superuser requires an email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)


        if not password:
            raise ValueError('Superuser must have a password.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
    
        return self.create_user(email_or_phone=email, username=username, password=password, **extra_fields)
    
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
        ('SMS', 'SMS'),
        ('WhatsApp', 'WhatsApp'),
        ('Email', 'Email'),
    ]


    username = models.CharField(_('username'), max_length=255, null=True, blank=True)
    user_role = models.CharField(_('user role'), max_length=50, choices=USER_ROLES)
    first_name = models.CharField(_('first name'), max_length=50)
    last_name = models.CharField(_('last_name'), max_length=50)
    email_or_phone = models.CharField(_('email or phone'), max_length=255, unique=True, validators=[validators.validate_email])
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    gender = models.CharField(_('gender'), max_length=10, choices=GENDER_CHOICES)
    #location = models.ForeignKey('Location', no_delete=models.SET_NULL, null=True)
    prefered_means_of_communication = models.CharField(_('prefered means of communication'), max_length=20, choices=COMMUNICATION_PREFERENCE)
    prefered_time_from = models.TimeField(_('prefered time from'), null=True, blank=True)
    prefered_time_to = models.TimeField(_('prefered time to'), null=True, blank=True)
    is_verified = models.BooleanField(_('is verified'), default=False)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Indicates if user account is active.'))
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email_or_phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    def get_short_name(self):
        return self.first_name.strip()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.user_role})'


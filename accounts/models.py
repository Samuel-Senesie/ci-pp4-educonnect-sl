from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
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
    user_role = models.CharField(max_length=50, choices=USER_ROLES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_or_phone = models.CharField(max_length=255, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    #location = models.ForeignKey('Location', no_delete=models.SET_NULL, null=True)
    prefered_means_of_communication = models.CharField(max_length=20, choices=COMMUNICATION_PREFERENCE)
    prefered_time_from = models.TimeField()
    prefered_time_to = models.TimeField()
    password = models.CharField(max_length=255),
    is_verified = models.BooleanField(default=False)
    verification_code = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.user_role})'


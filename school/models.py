from django.db import models
from django.utils.text import slugify
import uuid


# Create your models here.

class School(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ("Daycare", "Daycare"),
        ("Kindergarten", "Kindergarten"),
        ("Primary", "Primary"),
        ("JSS", "Junior Secondary School"),
        ("SSS", "Senior Secondary School"),
    ]

    OWNERSHIP_CHOICES = [
        ("Government", "Government"),
        ("Religious",  "Religious"),
        ("Community", "Community"),
        ("Private", "Private"),
        ("NGO", "NGO"),
        ("Other", "Other"),
    ]

    APPROVAL_STATUS_CHOICES = [
        ("Approved", "Approved"),
        ("Not Approved", "Not Approved"),
        ("Pending", "Pending"),
    ]

    SINGLE_OR_MIXED_CHOICES = [
        ("Single", "Single"),
        ("Mixed", "Mixed"),
    ]

    school_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    education_level = models.CharField(
        max_length=50, choices=EDUCATION_LEVEL_CHOICES, default="Primary"
    )
    owner = models.CharField(max_length=50, choices=OWNERSHIP_CHOICES, default="Private")
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS_CHOICES, 
        default="Pending",
    )
    emis_code = models.CharField(max_length=50, null=True, blank=True)
    single_or_mixed = models.CharField(
        max_length=10, choices=SINGLE_OR_MIXED_CHOICES, default="Mixed"
    )
    email_or_phone = models.CharField(max_length=100, unique=True)

    # Location Fields
    home_address = models.CharField(max_length=255, null=True, blank=True)
    chiefdom = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    # Admin Information
    admin_first_name = models.CharField(max_length=100)
    admin_last_name = models.CharField(max_length=100)
    admin_role = models.CharField(max_length=100, default="Schoold Administrator")

    #Communication preference
    preferred_means_of_communication = models.CharField(
        max_length=50, choices=[("SMS", "SMS"), ("WhatsApp", "WhatsApp"), ("Email", "Email")], default="Email"
    )
    preferred_time_from = models.TimeField(null=True, blank=True)
    preferred_time_to = models.TimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "School"
        verbose_name_plural = "Schools"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.school_id})"

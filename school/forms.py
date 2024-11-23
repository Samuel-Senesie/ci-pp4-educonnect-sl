from django import forms
from .models import School

class SchoolRegistrationForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            "name",
            "education_level",
            "owner",
            "approval_status",
            "single_or_mixed",
            "home_address",
            "chiefdom",
            "town",
            "district",
            "region",
            "email_or_phone",
            "admin_last_name",
            "admin_first_name",
            "preferred_means_of_communication",
            "preferred_time_from",
            "preferred_time_to",
        ]
    def clean_email_or_phone(self):
        data = self.cleaned_data["email_or_phone"]
        if School.objects.filter(email_or_phone=data).exists():
            raise forms.ValidationError("A school with this email/phone already exists.")
        return data

class SchoolAccessForm(forms.Form):
    school_id = forms.UUIDField(required=True, label="School ID")
    full_name = forms.CharField(required=True, max_length=100, label="Full Name")
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
        max_length=100,
        label="Password"
    )

    def clean_school_id(self):
        school_id = self.cleaned_data['school_id']
        if not School.objects.filter(school_id=school_id).exists():
            raise forms.ValidationError("Invalid School ID. Please scheck and try again.")
        return school_id

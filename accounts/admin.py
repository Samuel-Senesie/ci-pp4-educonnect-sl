from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.

# Custom UserAdmin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # List view in admin
    list_display = ('email_or_phone', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'user_role')

    #fields to display in detail view
    fieldsets = (
        (None, {'fields': ('email_or_phone', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'user_role' )}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('email_or_phone', 'password1', 'password2', 'first_name', 'last_name', 'date_of_birth', 'user_role', 'is_active')}
        ),
    )

    # Searchable fields in admin
    search_fields = ('email_or_phone',)
    ordering = ('email_or_phone',)

# Registering models in admin panel
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)
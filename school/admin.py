from django.contrib import admin
from .models import School

# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "education_level", "owner", "approval_status", "created_at")
    list_filter = ("education_level", "owner", "approval_status", "single_or_mixed")
    search_fields = ("name", "emis_code", "admin_first_name", "admin_last_name")
    prepopulated_fields = {"slug": ("name",)}


# Generated by Django 4.2.16 on 2024-11-17 16:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('username', models.CharField(blank=True, max_length=255, null=True, verbose_name='username')),
                ('user_role', models.CharField(choices=[('Parent', 'Parent'), ('Teacher', 'Teacher'), ('Administrator', 'Administrator'), ('Police', 'Police'), ('MCA', 'MCA')], max_length=50, verbose_name='user role')),
                ('first_name', models.CharField(max_length=50, verbose_name='first name')),
                ('last_name', models.CharField(max_length=50, verbose_name='last name')),
                ('email_or_phone', models.CharField(max_length=255, unique=True, verbose_name='email or phone')),
                ('is_parent', models.BooleanField(default=False)),
                ('is_school_staff', models.BooleanField(default=False)),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='date of birth')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10, verbose_name='gender')),
                ('preferred_means_of_communication', models.CharField(choices=[('sms', 'SMS'), ('email', 'Email'), ('whatsapp', 'WhatsApp')], default='sms', max_length=20, verbose_name='preferred means of communication')),
                ('preferred_time_from', models.TimeField(blank=True, null=True, verbose_name='preferred time from')),
                ('preferred_time_to', models.TimeField(blank=True, null=True, verbose_name='preferred time to')),
                ('is_verified', models.BooleanField(default=False, verbose_name='is verified')),
                ('verification_code', models.CharField(blank=True, max_length=10, null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Indicates if user account is active.', verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designate that this user has all the permisions without explicity assigning them.', verbose_name='superuser status')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('profile_id', models.AutoField(primary_key=True, serialize=False)),
                ('bio', models.TextField(blank=True, max_length=500, null=True, verbose_name='bio')),
                ('profile_picture', models.ImageField(blank=True, default='profile_pics/default_profile_pic.jpeg', null=True, upload_to='profile_pics/', verbose_name='profile picture')),
                ('background_image', models.ImageField(blank=True, default='background_images/default_background_image.jpeg', null=True, upload_to='background_images/', verbose_name='background image')),
                ('location', models.CharField(blank=True, max_length=100, null=True, verbose_name='location')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'ordering': ['user__last_name'],
            },
        ),
    ]

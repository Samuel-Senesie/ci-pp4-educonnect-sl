# Generated by Django 4.2.16 on 2024-11-23 02:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('school_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('education_level', models.CharField(choices=[('Daycare', 'Daycare'), ('Kindergarten', 'Kindergarten'), ('Primary', 'Primary'), ('JSS', 'Junior Secondary School'), ('SSS', 'Senior Secondary School')], default='Primary', max_length=50)),
                ('owner', models.CharField(choices=[('Government', 'Government'), ('Religious', 'Religious'), ('Community', 'Community'), ('Private', 'Private'), ('NGO', 'NGO'), ('Other', 'Other')], default='Private', max_length=50)),
                ('approval_status', models.CharField(choices=[('Approved', 'Approved'), ('Not Approved', 'Not Approved'), ('Pending', 'Pending')], default='Pending', max_length=20)),
                ('emis_code', models.CharField(blank=True, max_length=50, null=True)),
                ('single_or_mixed', models.CharField(choices=[('Single', 'Single'), ('Mixed', 'Mixed')], default='Mixed', max_length=10)),
                ('email_or_phone', models.CharField(max_length=100, unique=True)),
                ('home_address', models.CharField(blank=True, max_length=255, null=True)),
                ('chiefdom', models.CharField(blank=True, max_length=100, null=True)),
                ('town', models.CharField(blank=True, max_length=100, null=True)),
                ('district', models.CharField(blank=True, max_length=100, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('admin_first_name', models.CharField(max_length=100)),
                ('admin_last_name', models.CharField(max_length=100)),
                ('admin_role', models.CharField(default='Schoold Administrator', max_length=100)),
                ('preferred_means_of_communication', models.CharField(choices=[('SMS', 'SMS'), ('WhatsApp', 'WhatsApp'), ('Email', 'Email')], default='Email', max_length=50)),
                ('preferred_time_from', models.TimeField(blank=True, null=True)),
                ('preferred_time_to', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'School',
                'verbose_name_plural': 'Schools',
                'ordering': ['name'],
            },
        ),
    ]

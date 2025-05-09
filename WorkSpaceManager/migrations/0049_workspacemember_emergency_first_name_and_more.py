# Generated by Django 5.1 on 2025-04-19 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkSpaceManager', '0048_workspacemember_job_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacemember',
            name='emergency_first_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='emergency_last_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='emergency_phone_number',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='emergency_relationship',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='is_emergency_information',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.1 on 2024-11-19 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserManager', '0028_useraccount_current_workspace_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccount',
            name='customer',
        ),
    ]

# Generated by Django 5.1.6 on 2025-03-09 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkSpaceManager', '0040_workspacemember_company_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workspacemember',
            name='company_name',
        ),
        migrations.AddField(
            model_name='workspace',
            name='company_name',
            field=models.CharField(max_length=55, null=True),
        ),
    ]

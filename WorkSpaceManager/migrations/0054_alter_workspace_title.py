# Generated by Django 5.1 on 2025-04-26 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkSpaceManager', '0053_workspacemember_education_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspace',
            name='title',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]

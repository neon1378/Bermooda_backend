# Generated by Django 5.1 on 2025-02-17 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrmCore', '0043_alter_campaignfield_field_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaignform',
            name='fullname',
            field=models.CharField(max_length=100, null=True),
        ),
    ]

# Generated by Django 5.1 on 2024-12-23 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupportManager', '0011_alter_anoncustomer_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='workspace',
        ),
        migrations.AlterField(
            model_name='anoncustomer',
            name='phone_number',
            field=models.CharField(max_length=27, null=True, unique=True),
        ),
    ]

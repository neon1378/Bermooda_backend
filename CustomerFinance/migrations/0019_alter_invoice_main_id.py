# Generated by Django 5.1.6 on 2025-03-10 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomerFinance', '0018_alter_invoice_main_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='main_id',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
    ]

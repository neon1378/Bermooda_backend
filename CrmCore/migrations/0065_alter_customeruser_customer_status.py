# Generated by Django 5.1.6 on 2025-04-03 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrmCore', '0064_customeruser_customer_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeruser',
            name='customer_status',
            field=models.CharField(choices=[('dont_followed', 'Dont Followed'), ('follow_in_another_time', 'Follow In Another Time'), ('successful_sell', 'Successful Sell')], max_length=30, null=True),
        ),
    ]

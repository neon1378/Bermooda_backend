# Generated by Django 5.1.6 on 2025-04-07 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WalletManager', '0009_wallettransaction_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='payment_method',
            field=models.CharField(choices=[('WALLET', 'wallet'), ('PLAN', 'plan')], default='wallet', max_length=30, null=True),
        ),
    ]

# Generated by Django 5.1 on 2025-01-05 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WalletManager', '0004_remove_wallettransaction_user_account_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='card_number',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='order_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='paid_at',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='status_deposit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='track_id',
            field=models.TextField(null=True),
        ),
    ]

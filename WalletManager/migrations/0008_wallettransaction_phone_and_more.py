# Generated by Django 5.1.6 on 2025-03-18 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WalletManager', '0007_alter_wallet_workspace'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='phone',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='trans_action_status',
            field=models.CharField(choices=[('deposit', 'DEPOSIT'), ('decrease', 'DECREASE'), ('decreasesms', 'DECREASESMS'), ('decreasesmsline', 'DECREASESMSLINE')], max_length=60, null=True),
        ),
    ]

# Generated by Django 5.1 on 2024-12-24 14:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManager', '0036_remove_useraccount_fcm_token_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fcmtoken',
            name='token',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='fcmtoken',
            name='user_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fcm_tokens', to=settings.AUTH_USER_MODEL),
        ),
    ]

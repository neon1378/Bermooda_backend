# Generated by Django 5.1 on 2024-12-30 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Notification', '0002_notification_is_read_alter_notification_user_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]

# Generated by Django 5.1 on 2024-11-16 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MailManager', '0003_alter_message_main_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagelabel',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]

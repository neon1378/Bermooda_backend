# Generated by Django 5.1 on 2024-11-09 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupportManager', '0006_alter_roommessage_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roommessage',
            name='message_type',
            field=models.CharField(choices=[('anonymos', 'ANONYMOS'), ('operator', 'OPERATOR')], max_length=40, null=True),
        ),
    ]

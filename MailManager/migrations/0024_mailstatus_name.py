# Generated by Django 5.1 on 2025-02-11 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MailManager', '0023_categorydraft_draft'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailstatus',
            name='name',
            field=models.CharField(max_length=500, null=True),
        ),
    ]

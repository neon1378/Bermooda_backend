# Generated by Django 5.1 on 2024-12-26 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkSpaceManager', '0018_workspacemember_fullname'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspace',
            name='jadoo_workspace_id',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]

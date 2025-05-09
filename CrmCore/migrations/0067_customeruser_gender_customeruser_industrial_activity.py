# Generated by Django 5.1.6 on 2025-04-09 10:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrmCore', '0066_category_group_crm'),
        ('WorkSpaceManager', '0045_workspace_plan_started_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeruser',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'MALE'), ('female', 'FEMALE')], max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='industrial_activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='WorkSpaceManager.industrialactivity'),
        ),
    ]

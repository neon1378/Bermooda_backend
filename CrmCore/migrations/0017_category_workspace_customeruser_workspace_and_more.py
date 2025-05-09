# Generated by Django 5.1 on 2024-11-23 20:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrmCore', '0016_report_author_report_created'),
        ('WorkSpaceManager', '0009_remove_workspace_category_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='workspace',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_customer', to='WorkSpaceManager.workspace'),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='workspace',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='WorkSpaceManager.workspace'),
        ),
        migrations.AddField(
            model_name='label',
            name='workspace',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='label_customer', to='WorkSpaceManager.workspace'),
        ),
    ]

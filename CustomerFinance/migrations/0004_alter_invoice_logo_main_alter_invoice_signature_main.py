# Generated by Django 5.1 on 2024-11-14 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomerFinance', '0003_remove_invoice_logo_remove_invoice_signature'),
        ('core', '0006_mainfile_created_mainfile_workspace_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='logo_main',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_logo', to='core.mainfile'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='signature_main',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_signature', to='core.mainfile'),
        ),
    ]

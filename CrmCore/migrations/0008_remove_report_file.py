# Generated by Django 5.1 on 2024-11-13 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CrmCore', '0007_report_main_file_alter_report_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='file',
        ),
    ]

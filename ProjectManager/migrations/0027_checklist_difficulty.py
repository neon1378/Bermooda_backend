# Generated by Django 5.1.6 on 2025-02-22 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManager', '0026_alter_tasklabel_options_tasklabel_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='difficulty',
            field=models.IntegerField(default=1),
        ),
    ]

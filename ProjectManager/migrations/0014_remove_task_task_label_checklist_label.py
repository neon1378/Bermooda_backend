# Generated by Django 5.1 on 2024-11-30 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManager', '0013_remove_project_category_project_remove_project_task_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='task_label',
        ),
        migrations.AddField(
            model_name='checklist',
            name='label',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ProjectManager.tasklabel'),
        ),
    ]

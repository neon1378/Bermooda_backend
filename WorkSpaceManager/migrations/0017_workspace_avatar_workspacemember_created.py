# Generated by Django 5.1 on 2024-12-02 11:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkSpaceManager', '0016_maincategory_workspace_main_category_subcategory_and_more'),
        ('core', '0006_mainfile_created_mainfile_workspace_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspace',
            name='avatar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.mainfile'),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]

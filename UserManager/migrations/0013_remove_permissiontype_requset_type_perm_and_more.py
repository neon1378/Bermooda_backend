# Generated by Django 5.1 on 2024-11-08 10:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManager', '0012_permissioncategory_class_name_permissiontype'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissiontype',
            name='requset_type_perm',
        ),
        migrations.AddField(
            model_name='permissiontype',
            name='permission_type',
            field=models.CharField(choices=[('read', 'READ'), ('edit', 'EDIT'), ('manager', 'MANAGER')], max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='permissiontype',
            name='group_obj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gp_perm_type', to='auth.group'),
        ),
    ]

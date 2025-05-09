# Generated by Django 5.1 on 2024-12-16 16:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupportManager', '0009_categoryroom_workspace_room_workspace'),
        ('WorkSpaceManager', '0018_workspacemember_fullname'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='category_room',
        ),
        migrations.RemoveField(
            model_name='anoncustomer',
            name='refrence_id',
        ),
        migrations.AddField(
            model_name='room',
            name='activated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anoncustomer',
            name='phone_number',
            field=models.CharField(max_length=27, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_status',
            field=models.CharField(choices=[('WAITING', 'waiting'), ('CLOSED', 'closed'), ('CONFIRMED', 'confirmed')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='user_owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='roommessage',
            name='anonymous_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='SupportManager.anoncustomer'),
        ),
        migrations.AlterField(
            model_name='roommessage',
            name='message_type',
            field=models.CharField(choices=[('anonymous', 'ANONYMOUS'), ('operator', 'OPERATOR')], max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='roommessage',
            name='operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=55, null=True)),
                ('color_code', models.CharField(max_length=55, null=True)),
                ('members', models.ManyToManyField(related_name='departments', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='WorkSpaceManager.workspace')),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='SupportManager.department'),
        ),
        migrations.DeleteModel(
            name='CategoryRoom',
        ),
    ]

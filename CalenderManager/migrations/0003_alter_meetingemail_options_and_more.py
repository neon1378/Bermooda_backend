# Generated by Django 5.1.6 on 2025-04-12 04:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CalenderManager', '0002_meeting_meetingemail_meetinghashtag_meetingmembers_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meetingemail',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='meetinghashtag',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='meetingmembers',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='meetingphonenumber',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='reaped_status',
        ),
        migrations.AddField(
            model_name='meetingemail',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At'),
        ),
        migrations.AddField(
            model_name='meetingemail',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='Date and time when this record was soft deleted', null=True, verbose_name='Deleted At'),
        ),
        migrations.AddField(
            model_name='meetingemail',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Designates whether this record is soft deleted', verbose_name='Is Deleted'),
        ),
        migrations.AddField(
            model_name='meetingemail',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated At'),
        ),
        migrations.AddField(
            model_name='meetinghashtag',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At'),
        ),
        migrations.AddField(
            model_name='meetinghashtag',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='Date and time when this record was soft deleted', null=True, verbose_name='Deleted At'),
        ),
        migrations.AddField(
            model_name='meetinghashtag',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Designates whether this record is soft deleted', verbose_name='Is Deleted'),
        ),
        migrations.AddField(
            model_name='meetinghashtag',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated At'),
        ),
        migrations.AddField(
            model_name='meetingmembers',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At'),
        ),
        migrations.AddField(
            model_name='meetingmembers',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='Date and time when this record was soft deleted', null=True, verbose_name='Deleted At'),
        ),
        migrations.AddField(
            model_name='meetingmembers',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Designates whether this record is soft deleted', verbose_name='Is Deleted'),
        ),
        migrations.AddField(
            model_name='meetingmembers',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated At'),
        ),
        migrations.AddField(
            model_name='meetingphonenumber',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At'),
        ),
        migrations.AddField(
            model_name='meetingphonenumber',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='Date and time when this record was soft deleted', null=True, verbose_name='Deleted At'),
        ),
        migrations.AddField(
            model_name='meetingphonenumber',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Designates whether this record is soft deleted', verbose_name='Is Deleted'),
        ),
        migrations.AddField(
            model_name='meetingphonenumber',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated At'),
        ),
        migrations.AddIndex(
            model_name='meetingemail',
            index=models.Index(fields=['is_deleted'], name='CalenderMan_is_dele_8d53a2_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingemail',
            index=models.Index(fields=['deleted_at'], name='CalenderMan_deleted_8ec3e3_idx'),
        ),
        migrations.AddIndex(
            model_name='meetinghashtag',
            index=models.Index(fields=['is_deleted'], name='CalenderMan_is_dele_569a3d_idx'),
        ),
        migrations.AddIndex(
            model_name='meetinghashtag',
            index=models.Index(fields=['deleted_at'], name='CalenderMan_deleted_6cd148_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingmembers',
            index=models.Index(fields=['is_deleted'], name='CalenderMan_is_dele_3fceae_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingmembers',
            index=models.Index(fields=['deleted_at'], name='CalenderMan_deleted_80f4dd_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingphonenumber',
            index=models.Index(fields=['is_deleted'], name='CalenderMan_is_dele_6ea7bb_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingphonenumber',
            index=models.Index(fields=['deleted_at'], name='CalenderMan_deleted_2483fd_idx'),
        ),
    ]

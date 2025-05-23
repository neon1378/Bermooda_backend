# Generated by Django 5.1.6 on 2025-04-08 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0007_appupdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='Designates whether this record is soft deleted', verbose_name='Is Deleted')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Date and time when this record was soft deleted', null=True, verbose_name='Deleted At')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated At')),
                ('title', models.CharField(max_length=50, null=True)),
                ('date_to_start', models.DateField(null=True)),
                ('remember_type', models.CharField(choices=[('hour', 'HOUR'), ('minute', 'MINUTE'), ('day', 'day')], max_length=50, null=True)),
                ('remember_time', models.IntegerField(default=0)),
                ('files', models.ManyToManyField(to='core.mainfile')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'indexes': [models.Index(fields=['is_deleted'], name='CalenderMan_is_dele_1d833c_idx'), models.Index(fields=['deleted_at'], name='CalenderMan_deleted_a25355_idx')],
            },
        ),
    ]

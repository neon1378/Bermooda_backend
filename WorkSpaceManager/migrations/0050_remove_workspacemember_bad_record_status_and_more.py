# Generated by Django 5.1 on 2025-04-21 07:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkSpaceManager', '0049_workspacemember_emergency_first_name_and_more'),
        ('core', '0009_mainfile_original_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workspacemember',
            name='bad_record_status',
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='bad_records',
            field=models.ManyToManyField(related_name='member_bad_records', to='core.mainfile'),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='exempt_type',
            field=models.CharField(blank=True, choices=[('medicine', 'MEDICINE'), ('sponsorship', 'SPONSORSHIP'), ('education', 'EDUCATION'), ('sacrifice', 'SACRIFICE')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='insurance_type',
            field=models.CharField(blank=True, choices=[('tamin_ejtemaei', 'Tamin Ejtemaei'), ('takmili', 'Takmili'), ('bazneshastegi', 'Bazneshastegi'), ('darmani', 'Darmani'), ('hekmat', 'Hekmat'), ('nobat', 'Nobat'), ('other', 'Other')], max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='military_status',
            field=models.CharField(blank=True, choices=[('subject_to_service', 'Subject To Service'), ('exempt_from_service', 'Exempt From Service'), ('end_of_service', 'End Of Service'), ('in_the_service', 'In The Service')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='workspacemember',
            name='phone_number_static',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='workspacemember',
            name='avatar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_avatar', to='core.mainfile'),
        ),
    ]

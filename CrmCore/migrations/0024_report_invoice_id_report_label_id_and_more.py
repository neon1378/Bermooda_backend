# Generated by Django 5.1 on 2024-11-25 14:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrmCore', '0023_alter_customeruser_website'),
        ('core', '0006_mainfile_created_mainfile_workspace_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='invoice_id',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='label_id',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='payment_description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='payment_method',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='payment_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='تومان'),
        ),
        migrations.AddField(
            model_name='report',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='report',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='report',
            name='main_file',
        ),
        migrations.AddField(
            model_name='report',
            name='main_file',
            field=models.ManyToManyField(to='core.mainfile'),
        ),
    ]

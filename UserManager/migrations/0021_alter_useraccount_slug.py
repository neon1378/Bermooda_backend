# Generated by Django 5.1 on 2024-11-09 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManager', '0020_useraccount_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]

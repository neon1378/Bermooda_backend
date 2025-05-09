# Generated by Django 5.1 on 2025-01-20 13:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MailManager', '0020_remove_favoritemail_content_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MailAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('mail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mail_actions', to='MailManager.mail')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

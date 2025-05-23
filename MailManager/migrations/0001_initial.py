# Generated by Django 5.1 on 2024-10-28 08:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=50, null=True)),
                ('color_code', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(null=True)),
                ('file', models.FileField(null=True, upload_to='main_files/file')),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('read_status', models.BooleanField(default=False)),
                ('message_reciver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_reciver_m', to=settings.AUTH_USER_MODEL)),
                ('message_sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_sender_m', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, null=True)),
                ('status_pending', models.BooleanField(default=False)),
                ('send_time', models.DateTimeField(null=True)),
                ('createor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='createor_conversation', to=settings.AUTH_USER_MODEL)),
                ('reciver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reciver_conversation', to=settings.AUTH_USER_MODEL)),
                ('message', models.ManyToManyField(blank=True, to='MailManager.message')),
                ('conversation_label', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='MailManager.messagelabel')),
            ],
        ),
    ]

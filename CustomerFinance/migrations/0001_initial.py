# Generated by Django 5.1 on 2024-10-28 08:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_city_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, null=True)),
                ('count', models.PositiveIntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, null=True, verbose_name='تومان')),
            ],
        ),
        migrations.CreateModel(
            name='Information',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname_or_company_name', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('address', models.TextField(null=True)),
                ('phone_number', models.CharField(max_length=40, null=True)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='city_buyer', to='core.city')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='state_buyer', to='core.city')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, null=True)),
                ('description', models.TextField(null=True)),
                ('signature', models.ImageField(upload_to='customer/factors/signatures')),
                ('logo', models.ImageField(upload_to='customer/factors/logos')),
                ('discount', models.PositiveIntegerField(default=0)),
                ('taxes', models.PositiveIntegerField(default=0)),
                ('created', models.DateField(auto_now_add=True)),
                ('invoice_code', models.CharField(max_length=90, null=True)),
                ('buyer_information', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='information_buyer', to='CustomerFinance.information')),
                ('seller_information', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='information_seller', to='CustomerFinance.information')),
                ('product', models.ManyToManyField(to='CustomerFinance.productinvoice')),
            ],
        ),
    ]

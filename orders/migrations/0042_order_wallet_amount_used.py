# Generated by Django 5.1.3 on 2025-01-19 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0041_alter_orderproduct_status_alter_returnproduct_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='wallet_amount_used',
            field=models.FloatField(default=0.0),
        ),
    ]

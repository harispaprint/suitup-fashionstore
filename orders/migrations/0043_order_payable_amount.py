# Generated by Django 5.1.3 on 2025-02-03 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0042_order_wallet_amount_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payable_amount',
            field=models.FloatField(default=0.0),
        ),
    ]

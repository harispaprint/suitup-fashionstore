# Generated by Django 5.1.3 on 2025-02-05 02:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0044_remove_order_payment_payment_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_order', to='orders.order'),
        ),
    ]

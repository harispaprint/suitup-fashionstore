# Generated by Django 5.1.3 on 2025-01-08 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_order_coupon_order_net_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='status',
            field=models.CharField(choices=[('Confirmed', 'confirmed'), ('Shipped', 'shipped'), ('Delivered', 'delivered'), ('Cancelled', 'cancelled'), ('Return', 'return')], default='confirmed', max_length=10),
        ),
    ]

# Generated by Django 5.1.3 on 2025-01-11 12:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0008_remove_cartitem_variations'),
        ('orders', '0020_alter_couponhistory_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponhistory',
            name='cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='carts.cart'),
        ),
    ]

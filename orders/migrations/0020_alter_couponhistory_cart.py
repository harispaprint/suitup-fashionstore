# Generated by Django 5.1.3 on 2025-01-11 09:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0008_remove_cartitem_variations'),
        ('orders', '0019_couponhistory_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponhistory',
            name='cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='carts.cart'),
        ),
    ]

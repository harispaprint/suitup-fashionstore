# Generated by Django 5.1.3 on 2025-01-13 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_order_grand_order_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='sub_order_total',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]

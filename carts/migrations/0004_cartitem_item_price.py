# Generated by Django 5.1.3 on 2024-12-29 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_cartoffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='item_price',
            field=models.IntegerField(default=0),
        ),
    ]

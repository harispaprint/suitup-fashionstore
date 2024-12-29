# Generated by Django 5.1.3 on 2024-12-27 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_stock_search_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='variation_combo',
            field=models.ManyToManyField(related_name='product_variation_combo', to='store.variation'),
        ),
    ]

# Generated by Django 5.1.3 on 2025-01-09 01:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_wishlist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='variation',
            options={'ordering': ['variation_category']},
        ),
    ]

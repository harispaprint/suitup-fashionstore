# Generated by Django 5.1.3 on 2025-01-04 01:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_payment_payment_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='status',
            new_name='payment_verified',
        ),
    ]

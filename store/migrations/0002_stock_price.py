# Generated by Django 5.1.3 on 2024-12-24 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 5.1.3 on 2025-02-22 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddresses',
            name='pincode',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]

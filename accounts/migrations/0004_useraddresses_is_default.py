# Generated by Django 5.1.3 on 2024-12-12 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_useraddresses_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddresses',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
# Generated by Django 5.1.3 on 2025-01-14 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_rename_return_product_returnproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returnproduct',
            name='reason',
            field=models.CharField(choices=[('damaged', 'Damaged or Defective Product'), ('wrong_product', 'Wrong Product Delivered'), ('size_issue', 'Size or Fit Issues'), ('not_as_described', 'Product Not as Described'), ('missing_items', 'Missing Items'), ('quality_issue', 'Quality Issues'), ('performance_issue', 'Performance Issues'), ('expired_product', 'Expired Product'), ('change_of_mind', 'Change of Mind'), ('better_price', 'Better Price Available'), ('tampered_package', 'Package Tampered')], max_length=100),
        ),
    ]

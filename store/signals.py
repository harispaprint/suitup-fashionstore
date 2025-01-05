from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Stock


@receiver(m2m_changed, sender=Stock.variation_combo.through)
def set_search_key(sender, instance, action, **kwargs):
    if action == "post_add":
        variations = ", ".join([str(variation.variation_category.name)+str(variation.variation_value) for variation in instance.variation_combo.all()])
        instance.search_key = f"{instance.product.product_name}{variations}"
        instance.save()     
       
        

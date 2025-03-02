from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Stock
from django.db import transaction


@receiver(m2m_changed, sender=Stock.variation_combo.through)
def set_search_key(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        def update_search_key():
            variations = "-".join([str(variation.id) for variation in instance.variation_combo.all()])
            instance.search_key = f"{instance.product.id}-{variations}"
            instance.save(update_fields=['search_key'])

        transaction.on_commit(update_search_key)  # Ensure update after transaction commit


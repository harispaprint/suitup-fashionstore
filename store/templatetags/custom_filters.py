from django import template

register = template.Library()

@register.filter
def get_values(variation_set, variation_type):
    return variation_set.filter(variation_category=variation_type).values_list('variation_value', flat=True)
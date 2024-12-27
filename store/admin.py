from django.contrib import admin
from .models import Product,ProductImage, Stock,Variation, VariationCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

# class StockAdmin(admin.ModelAdmin):
#     def save_model(self, request, obj, form, change):
#         # Save the object first to get the instance and its ManyToMany relationships
#         super().save_model(request, obj, form, change)
        
#         # Now update the search_key field after saving
#         if not obj.search_key:
#             variations = "-".join(sorted([v.name for v in obj.variation_combo.all()]))
#             obj.search_key = f"{obj.product.product_name}-{variations}"
#             obj.save()  # Save the object again to update search_key

# Register the model with its admin class
admin.site.register(Stock)

# Register your models here.
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Variation, VariationAdmin)
admin.site.register(VariationCategory)


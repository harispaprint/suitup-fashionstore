from django.contrib import admin
from .models import Product,ProductImage,Variation

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('product_name',)}
    list_display = ('product_name','price','stock','category','modified_date')

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ('is_active',)

# Register your models here.
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Variation,VariationAdmin)

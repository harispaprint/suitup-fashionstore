from django.contrib import admin
from .models import Product,ProductImage, Stock,Variation, VariationCategory,ReviewsRatings,BulkPurchaseOffer,Coupon, Wishlist

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')



admin.site.register(Stock)

# Register your models here.
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Variation, VariationAdmin)
admin.site.register(VariationCategory)
admin.site.register(ReviewsRatings)
admin.site.register(Coupon)
admin.site.register(BulkPurchaseOffer)
admin.site.register(Wishlist)


from django.contrib import admin
from .models import CouponHistory, Payment,Order,OrderProduct, ReturnProduct, Wallet, WalletTransaction

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','tax', 'status','created_at','is_ordered']
    list_filter = ['status','is_ordered','created_at']
    search_fields = ['order_number']

class CouponHistoryAdmin(admin.ModelAdmin):
    list_display = ['user','cart','coupon','availed_date']

class ReturnProductAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'order_product', 'reason', 'status', 'created_date', 'updated_date']

    def get_user(self, obj):
        return obj.order_product.user  # Accessing related field
    get_user.short_description = 'User'  # Optional: Display name in the admin

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order','product','user','status']
  
   
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct,OrderProductAdmin)
admin.site.register(CouponHistory,CouponHistoryAdmin)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(ReturnProduct,ReturnProductAdmin)


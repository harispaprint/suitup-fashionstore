from django.contrib import admin
from .models import Cart,CartItem,CartOffer

# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','cart_id','user','date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','cart','quantity','is_active')

admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(CartOffer)


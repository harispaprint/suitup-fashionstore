from django.urls import path
from . import views

urlpatterns = [
    path('',views.cart,name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('increase_cart/<int:product_id>/<int:cart_item_id>',views.increase_cart,name='increase_cart'),
    path('reduce_cart/<int:product_id>/<int:cart_item_id>',views.reduce_cart,name='reduce_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>',views.remove_cart_item,name='remove_cart_item'),
    path('checkout/<int:cart_id>/',views.checkout,name='checkout'),
]

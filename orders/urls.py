from django.urls import path
from . import views


urlpatterns = [
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('my_orders/<slug:status>/', views.my_orders, name='my_orders'),
    path('product_cancel_request/<int:order_product_id>/', views.product_cancel_request, name='product_cancel_request'),
    path('product_return_request/<int:order_product_id>/', views.product_return_request, name='product_return_request'),
    
    path('place_order/',views.place_order,name='place_order'),
    path('payment/<int:order_id>/',views.payment,name='payment'),
    path("retry_failed_payment/<int:order_id>/", views.retry_failed_payment, name="retry_failed_payment"),
    path('payment_status/<str:order_id>/', views.payment_status, name='payment_status'),
    
    path('verify_payment/',views.verify_payment,name='verify_payment'),
    
    path('invoice/<int:order_id>/',views.invoice,name='invoice'),
    path('generate_invoice_pdf/<int:order_id>',views.generate_invoice_pdf,name="generate_invoice_pdf"),

    path('payment_cancelled/<int:order_id>/',views.payment_cancelled,name="payment-cancelled"),

    path('ordered_product_status/<int:order_product_id>/',views.ordered_product_status,name='ordered_product_status'),
    path('check_coupon/',views.check_coupon,name='check_coupon'),

    path('order_product_refund/<int:order_product_id>/',views.order_product_refund,name="order_product_refund")
   
]

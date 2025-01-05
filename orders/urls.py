from django.urls import path
from . import views


urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payment/',views.payment,name='payment'),
    path('payment_status/<str:order_id>/', views.payment_status, name='payment_status'),
    path('cancel_order_page/<int:order_id>/',views.cancel_order_page,name='cancel_order_page'),
    path('cancel_ordered_product/<int:ordered_product_id>/',views.cancel_ordered_product,name='cancel_ordered_product'),
    path('cancel_order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('verify_payment/',views.verify_payment,name='verify_payment'),
    path('invoice/',views.invoice,name='invoice'),
]

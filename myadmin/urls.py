from django.urls import path
from . import views



urlpatterns = [
    path('',views.admin_login,name='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    
    path('customer_management/',views.customer_management,name='customer_management'),
    path('delete_user/<int:user_id>',views.delete_user,name='delete_user'),
    path('deactivate_user/<int:user_id>',views.user_status_update,name='deactivate_user'),
    path('activate_user/<int:user_id>',views.user_status_update,name='activate_user'), 
    
    path('product_management/',views.product_management,name='product_management'),
    path('add_product',views.add_product,name='add_product'),
    path('add_product_variation/',views.add_product_variation,name='add_product_variation'),
    path('add_product_images/<int:product_id>',views.add_product_images,name='add_product_images'),
    path('edit_product/<int:product_id>',views.edit_product,name='edit_product'),
    path('deactivate_product/<int:product_id>',views.product_status_update,name='deactivate_product'),
    path('activate_product/<int:product_id>',views.product_status_update,name='activate_product'),

    path('category_management/',views.category_management,name='category_management'),
    path('add_category',views.add_category,name='add_category'),
    path('delete_category/<int:category_id>',views.delete_category,name='delete_category'),

    path('order_management/',views.order_management,name='order_management'),
    path('admin_cancel_order_page/<int:order_id>/',views.admin_cancel_order_page,name='admin_cancel_order_page'),
    path('admin_cancel_ordered_product/<int:ordered_product_id>/',views.admin_cancel_ordered_product,name='admin_cancel_ordered_product'),
    path('admin_cancel_order/<int:order_id>/',views.admin_cancel_order,name='admin_cancel_order'),

    path('inventory_management/',views.inventory_management,name='inventory_management'),
    path('add_product_stock/', views.add_product_stock, name='add_product_stock'),
    path('<int:pk>/update_product_stock/', views.update_product_stock, name='update_product_stock'),
    path('delete_stock/<int:stock_id>',views.delete_stock,name='delete_stock'),

    path('create-stock/', views.stock_create_view, name='create_stock'),
    path('load-variations/', views.load_variations, name='load_variations'),
    
    path('get-variations/<int:product_id>/', views.get_variations, name='get_variations'),
     path('my-view/', views.my_view, name='my-view'),

]

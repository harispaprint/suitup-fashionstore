from django.urls import path
from . import views


urlpatterns = [
    path('',views.admin_login,name='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('customer_management/',views.customer_management,name='customer_management'),
    path('product_management/',views.product_management,name='product_management'),
    path('category_management/',views.category_management,name='category_management'),
    path('delete_user/<int:user_id>',views.delete_user,name='delete_user'),
    path('deactivate_user/<int:user_id>',views.user_status_update,name='deactivate_user'),
    path('activate_user/<int:user_id>',views.user_status_update,name='activate_user'),
    path('add_product',views.add_product,name='add_product'),
    path('add_product_images/<int:product_id>',views.add_product_images,name='add_product_images'),
    path('edit_product/<int:product_id>',views.edit_product,name='edit_product'),
    path('deactivate_product/<int:product_id>',views.product_status_update,name='deactivate_product'),
    path('activate_product/<int:product_id>',views.product_status_update,name='activate_product'),
    path('add_category',views.add_category,name='add_category'),
    path('delete_category/<int:category_id>',views.delete_category,name='delete_category'),
]

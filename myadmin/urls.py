from django.urls import path
from . import views



urlpatterns = [
    path('',views.admin_login,name='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    
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
    # path('add_category',views.add_category,name='add_category'),
    path('delete_category/<int:category_id>',views.delete_category,name='delete_category'),
    path("add-category-ajax/", views.add_category_ajax, name="add_category_ajax"),

    path('order_management/',views.order_management,name='order_management'),
    path('update_order_product_status/<int:order_product_id>/', views.update_order_product_status, name='update_order_product_status'),
    path('admin_cancel_order_page/<int:order_id>/',views.admin_cancel_order_page,name='admin_cancel_order_page'),
    path('admin_cancel_ordered_product/<int:ordered_product_id>/',views.admin_cancel_ordered_product,name='admin_cancel_ordered_product'),
    path('admin_cancel_order/<int:order_id>/',views.admin_cancel_order,name='admin_cancel_order'),

    path('coupon_management/',views.coupon_management,name='coupon_management'),
    path('add_coupon/',views.add_coupon,name="add_coupon"),
    path('delete_coupon/<int:coupon_id>',views.delete_coupon,name='delete_coupon'),

    path('inventory_management/',views.inventory_management,name='inventory_management'),
    path('add_product_stock/<str:id>/', views.add_product_stock, name='add_product_stock'),
    path('update_product_stock/<int:variation_id>/', views.update_product_stock, name='update_product_stock'),
    path('update_product_price/<int:variation_id>/', views.update_product_price, name='update_product_price'),
    path('delete_stock/<int:stock_id>',views.delete_stock,name='delete_stock'),

    path('create-stock/', views.stock_create_view, name='create_stock'),
    path('load_variations/', views.load_variations, name='load_variations'),
    
    # path('get-variations/<int:product_id>/', views.get_variations, name='get_variations'),

    path('sales_report_filter/', views.sales_report_filter, name='sales_report_filter'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('order_product_return_decision/<int:order_product_id>/',views.order_product_return_decision,name="order_product_return_decision"),

    # path("export_pdf/", views.export_pdf, name="export_pdf"),
    path("export_excel/", views.export_excel, name="export_excel"),
    path('generate-pdf/<str:sale_date>/', views.generate_pdf_from_template, name='generate_pdf_from_template'),
]

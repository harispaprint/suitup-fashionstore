from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
    path('delete_product/<int:product_id>/',views.delete_product,name='delete_product'),
    path('search/',views.search,name='search'),
    path('check-stock/<int:product_id>/', views.check_stock, name='check_stock'),

    path('review/submit/<int:product_id>/',views.review_submit,name='review_submit'),
]


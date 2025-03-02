from django.urls import path
from . import views
from category.views import category,search_category

urlpatterns = [
    path('', views.store, name='store'),
    path('category/', category, name='category'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
    path('delete_product/<int:product_id>/',views.delete_product,name='delete_product'),
    path('search_product/',views.search_product,name='search_product'),
    path('search_category/',search_category,name='search_category'),
    path('check-stock/<int:product_id>/', views.check_stock, name='check_stock'),

    path('review/submit/<int:product_id>/',views.review_submit,name='review_submit'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('update_wishlist/<int:product_id>',views.update_wishlist,name='update_wishlist'),
    path('remove_wishlist/<int:product_id>',views.remove_wishlist,name='remove_wishlist'),
]


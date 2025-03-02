from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path("success/",views.success,name='success'),
    path('dashboard/',views.user_dashboard,name='user_dashboard'),
    path('email/', views.email_view, name='email_view'),
    
    path('edit_profile/', views.edit_profile, name='edit_profile'),
        
    path('saved_addresses/',views.saved_addresses,name='saved_addresses'),
    path('set_default_address/<int:address_id>/',views.set_default_address,name='set_default_address'),
    path('add_user_address/', views.add_user_address, name='add_user_address'),
    path('edit_user_address/<int:address_id>/', views.edit_user_address, name='edit_user_address'),
    path('delete_user_address/<int:address_id>/', views.delete_user_address, name='delete_user_address'),
    
    path('wallet/<slug:status>/',views.wallet,name='wallet'),
    path('wallet/',views.wallet,name='wallet'),

    
]

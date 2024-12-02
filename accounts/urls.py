from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path("success/",views.success,name='success'),
    path('send-otp/', views.send_otp_email, name='send_otp_email'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/',views.user_dashboard,name='user_dashboard')
]

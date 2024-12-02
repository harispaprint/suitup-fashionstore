
from django.core.cache import cache
from django.shortcuts import redirect, render,get_object_or_404
from accounts.models import Account
from store.models import Product
from .forms import RegistrationForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # cleaned_data = form.cleaned_data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()
            messages.success(request,'Registration Successful!')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form' : form
    }
    return render(request,'accounts/register.html',context)



def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        
        if user is not None:
            auth.login(request,user)
            messages.success(request,'Logged in Successfully')
            return redirect('user_dashboard')
        else:
            messages.error(request,'Invalid Credetials')
            return redirect('login')
    return render(request,'accounts/login.html')


@login_required(login_url = login)
def logout(request):
    auth.logout(request)
    messages.success(request,'Logged Out Successfully')
    return redirect('login')

def success(request):
    return render(request,'success.html')

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = generate_otp()

        # Save OTP to session or database
        request.session['email_otp'] = otp

        # Send OTP email
        subject = 'Your OTP Code'
        message = f'Your One-Time Password (OTP) is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return JsonResponse({'message': 'OTP sent successfully'})
    return render(request, 'send_otp.html')

def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('email_otp')

        if user_otp == session_otp:
            return JsonResponse({'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'message': 'Invalid OTP'}, status=400)
    return render(request, 'verify_otp.html')

@login_required(login_url = login)
def user_dashboard(request):
    return render(request,'accounts/user_dashboard.html')




from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404

from accounts.models import Account, UserAddresses, UserProfile
from .forms import RegistrationForm, UserAddressForm, UserForm, UserProfileForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.utils import _cart_id
from carts.models import Cart,CartItem
from orders.models import Order, OrderProduct
import requests


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

            #User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_mail = email
            send_mail = EmailMessage(mail_subject,message,to=[to_mail])
            send_mail.send()

            messages.success(request,'Thank you for registering with us, We have sent you verification link to your mail. Please verify it')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form' : form
    }
    return render(request,'accounts/register.html',context)

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Account successfully activated')
        userprofile = UserProfile.objects.create(user=user)
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=userprofile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'userprofile': userprofile,
        }
        return render(request, 'accounts/edit_profile.html', context)
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

def forgot_password(request):
    if request.method=='POST':
        email = request.POST['email']
        is_user_exist = Account.objects.filter(email=email).exists()
        if is_user_exist:
            user = Account.objects.get(email__exact=email)

            #password reset link 
            current_site = get_current_site(request)
            mail_subject = 'Password reset link'
            message = render_to_string('accounts/password_reset_email.html',{
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),
            })
            to_mail = email
            send_mail = EmailMessage(mail_subject,message,to=[to_mail])
            send_mail.send()

            messages.success(request,' We have sent you password reset link to your mail.')
            return redirect('login')
        else:
            messages.error(request,'account doesnot exists')
            return redirect('forgot_password')
    return render(request,'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                
                product_variation = []
                if is_cart_item_exist:     
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        product_variations_cart = item.variation.all()
                        product_variation.append(list(product_variations_cart))
                
                cart_item = CartItem.objects.filter(user=user)
                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variation.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)

                for pr_variation in product_variation:
                    if pr_variation in ex_var_list:
                        index = ex_var_list.index(pr_variation)
                        item_id = id[index]
                        item = CartItem.objects.get(id=item_id)
                        item.quantity+=1
                        item.user = user
                        item.save()
                    else:
                        cart_items = CartItem.objects.filter(cart=cart)
                        for item in cart_items:
                            item.user=user
                            item.save()
 
            except:
                pass    
            auth.login(request,user)
            messages.success(request,'Logged in Successfully')
            
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                return redirect(nextpage)
            except:
                pass
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

@login_required(login_url = login)
def user_dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/user_dashboard.html', context)

@login_required(login_url='login')
def edit_profile(request):
    
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
        }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def order_detail(request, order_id):
    
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    current_user = request.user
    cart_user = order.user
    if current_user is cart_user:
        for i in order_detail:
            subtotal += i.product_price * i.quantity

        context = {
            'order_detail': order_detail,
            'order': order,
            'subtotal': subtotal,
        }
        return render(request, 'accounts/order_detail.html', context)
    else:
        return redirect('store')

def saved_addresses(request):
    current_user = request.user
    saved_addresses = UserAddresses.objects.filter(user=current_user).order_by('-is_default')
    context = {
        'saved_addresses' : saved_addresses
    }
    return render(request,'accounts/saved_addresses.html',context)

def set_default_address(request,address_id):
    current_default = UserAddresses.objects.get(is_default=True)
    current_default.is_default=False
    current_default.save()
    new_default = UserAddresses.objects.get(id=address_id)
    new_default.is_default=True
    new_default.save()
    return redirect('saved_addresses')

@login_required(login_url='login')
def add_user_address(request):
    if request.method == 'POST':
        address_form = UserAddressForm(request.POST)
        if address_form.is_valid():
            useraddress = address_form.save(commit=False)
            useraddress.user = request.user
            address_form.save()
            messages.success(request, 'New address added succefully.')
            return redirect('saved_addresses')
    else:
        address_form = UserAddressForm()
    form_heading="Add Address"
    context = {
        'form_heading': form_heading,
        'address_form': address_form,
    }
    return render(request, 'accounts/user_address_form.html', context)

@login_required(login_url='login')
def edit_user_address(request,address_id):
    useraddress = UserAddresses.objects.get(user=request.user,id=address_id)
    if request.method == 'POST':
        address_form = UserAddressForm(request.POST, instance=useraddress)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, 'Your address has been updated.')
            return redirect('saved_addresses')
    else:
        address_form = UserAddressForm(instance=useraddress)
    form_heading="Edit Address"
    context = {
        'form_heading': form_heading,
        'address_form': address_form,
    }
    return render(request, 'accounts/user_address_form.html', context)



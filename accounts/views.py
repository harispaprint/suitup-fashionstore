
from django.core.cache import cache
from django.shortcuts import redirect, render,get_object_or_404
from orders.models import Order, OrderProduct
from accounts.models import Account, UserProfile
from .forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from carts.utils import _cart_id
from carts.models import Cart,CartItem
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
                # next_url = request.GET.get('next', '/')
                # return redirect(next_url)
        
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
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)


from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from orders.forms import OrderForm
from store.models import Product,Variation
from carts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from accounts.views import login
from .utils import _cart_id


def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation =[]
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
                
        #create or manage cart_item
        is_cart_item_exist = CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_item_exist:     
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            
            else:
                item = CartItem.objects.create(product=product,user=current_user,quantity = 1)
                if len(product_variation)>0:
                        item.variation.clear()
                        item.variation.add(*product_variation)
                        item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1,
            )
            if len(product_variation)>0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
    else:
        product_variation =[]
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
                
        #create or manage cart
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                    cart_id = _cart_id(request)
                )
            cart.save()     
        
        #create or manage cart_item
        is_cart_item_exist = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exist:     
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            
            else:
                item = CartItem.objects.create(product=product,cart=cart,quantity = 1)
                if len(product_variation)>0:
                        item.variation.clear()
                        item.variation.add(*product_variation)
                        item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1,
            )
            if len(product_variation)>0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
    


def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
             cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
            
    except Cart.DoesNotExist:
        total = quantity = cart_items = None
        
    context = {
            'total' : total,
            'quantity' : quantity,
            'cart_items' : cart_items,
            'tax' : tax,
            'grand_total' : grand_total,
        }       
    return render(request,'store/cart.html',context)

def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url = login)
def checkout(request,total=0,quantity=0,cart_items=None):
    current_user = request.user
    try:
        tax=0
        grand_total=0
        # cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(user=current_user,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
            
    except Cart.DoesNotExist:
        total = quantity = cart_items = None
        
    context = {
            'total' : total,
            'quantity' : quantity,
            'cart_items' : cart_items,
            'tax' : tax,
            'grand_total' : grand_total,
        }    
    return render(request,'store/checkout.html',context)
    
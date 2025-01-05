from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.utils import get_search_key
from accounts.models import UserAddresses
# from orders.forms import OrderForm
from store.models import BulkPurchaseOffer, Product, Stock,Variation
from carts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from accounts.views import login
from .utils import _cart_id


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    search_key = get_search_key(product,request)
    print(f"search key {search_key}")
    stock = Stock.objects.filter(search_key__iexact=search_key).first()
    print(f"stock object - {stock}")

    # If the user is authenticated
    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(stock=stock, user=current_user).exists()
        print(f"is_cart_item_exists {is_cart_item_exists}")
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(stock=stock, user=current_user).first()
            max_qty=cart_item.product.stock//5
            if cart_item.quantity<max_qty:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.info(request,'Product max quantity exceeded!')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
                stock=stock
            )
            cart_item.save()
            if cart_item.quantity==1:
                messages.success(request,'Product added to cart Successfully!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    # If the user is not authenticated
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
            
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
           
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(stock=stock, cart=cart).exists()
        print(f"is_cart_item_exists {is_cart_item_exists}")
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(stock=stock, cart=cart).first()
            max_qty=cart_item.product.stock//2
            if cart_item.quantity<max_qty:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.info(request,'Product max quantity exceeded!')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart=cart,
                stock=stock
            )
            cart_item.save()
            if cart_item.quantity==1:
                messages.success(request,'Product added to cart Successfully!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

def cart(request,total=0,quantity=0,discount=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        total_savings=0
        if request.user.is_authenticated:
             cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            print(f"cart_item {cart_item}")
            item_price = cart_item.stock.price
            offer = BulkPurchaseOffer.objects.filter(product=cart_item.product).first()
            print(offer)
            if offer is not None:
                discount = offer.current_discount(cart_item.quantity)
            else:
                discount = 0
            d_item_price = round(item_price*(1-discount/100),2)
            savings = round((item_price - d_item_price)*cart_item.quantity,2)

            cart_item.discount = discount
            cart_item.d_item_price = d_item_price
            cart_item.savings = savings
            cart_item.save()

            total += round(d_item_price*cart_item.quantity,2)
            total_savings += savings
            quantity += cart_item.quantity

        tax = round((2*total)/100,2)
        grand_total = round(total + tax,2)
            
    except Cart.DoesNotExist:
        total = quantity = cart_items = None
    context = {
            'total' : total,
            'total_savings' : total_savings,
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
    user_addresses = UserAddresses.objects.filter(user=current_user)
    try:
        tax=0
        grand_total=0
        # cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(user=current_user,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.stock.price*cart_item.quantity)
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
            'user_addresses':user_addresses,
        }    
    return render(request,'store/checkout.html',context)
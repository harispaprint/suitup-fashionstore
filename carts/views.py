import json
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from orders.models import CouponHistory
from store.utils import get_search_key
from accounts.models import UserAddresses
# from orders.forms import OrderForm
from store.models import BulkPurchaseOffer, Coupon, Product, Stock,Variation, Wishlist
from carts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from accounts.views import login
from .utils import _cart_id,get_user_cart_id
from django.core.serializers import serialize



def add_cart(request, product_id,cart=None):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    search_key = get_search_key(product,request)
    stock = Stock.objects.filter(search_key__iexact=search_key).first()

    # If the user is authenticated
    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(stock=stock, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(stock=stock, user=current_user).first()

            if cart_item.quantity < stock.product_stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.info(request,'Product max quantity exceeded!')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            try:
                cart = Cart.objects.get(user=current_user,is_purchased=False) # get the cart using the cart_id present in the session
            
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id = _cart_id(request),user=current_user)
            cart.save()
            cart_item = CartItem.objects.create(product = product,quantity = 1, user = current_user,cart=cart, stock=stock)
            cart_item.save()
            #check product added to cart is there is wishlist, then delete it from wishlist
            try:
                wishlist = Wishlist.objects.get(user= current_user,product=cart_item.product)
                wishlist.delete()
            except Wishlist.DoesNotExist:
                pass

            if cart_item.quantity==1:
                messages.success(request,'Product added to cart Successfully!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    # If the user is not authenticated
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
            
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
           
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(stock=stock, cart=cart).exists()
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

def cart(request,sub_total=0,quantity=0,discount=0,cart_items=None,cart=None):
    url = request.META.get('HTTP_REFERER')
    try:
        tax=0
        grand_total=0
        total_savings=0
        if request.user.is_authenticated:
             cart_items = CartItem.objects.filter(user=request.user,is_active=True)
             
             if cart_items.first() is not None:
                cart = cart_items.first().cart
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)


        for cart_item in cart_items:
            item_price = cart_item.stock.price
            offer = BulkPurchaseOffer.objects.filter(product=cart_item.product).first()
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

            sub_total += round(d_item_price*cart_item.quantity,2)
            total_savings += savings
            quantity += cart_item.quantity

        tax = round((2*sub_total)/100,2)
        grand_total = round(sub_total + tax,2)
            
    except Cart.DoesNotExist:
        total = quantity = cart_items = None
    context = {
            'sub_total' : sub_total,
            'total_savings' : total_savings,
            'quantity' : quantity,
            'tax' : tax,
            'grand_total' : grand_total,
            'cart_items' : cart_items,
            'cart' : cart,
        }
   
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if AJAX request
        cart_item_id = request.GET.get('cartItemId')  # Retrieve cartItemId from the request
        cart_id = None
        cart_quantity = 0
        d_item_price = 0
        discount = 0
        if cart_items.exists():
            try:
                cart_item_updated = cart_items.get(id=cart_item_id)
                cart_id = cart_item_updated.id
                cart_quantity = cart_item_updated.quantity
                d_item_price = cart_item_updated.d_item_price
                discount = cart_item_updated.discount
            except CartItem.DoesNotExist:
                pass
        else:
            pass
        context1 = {
            'sub_total' : sub_total,
            'total_savings' : total_savings,
            'quantity' : quantity,
            'tax' : tax,
            'grand_total' : grand_total,
            'cart_quantity' : cart_quantity,
            'd_item_price' : d_item_price,
            'discount' : discount,
        }
        return JsonResponse(context1,status=200)
   
    if 'cart' in url:      
        return render(request,'store/cart.html',context)
    else:
         return render(request,'store/cart.html',context)
    
def increase_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
            cart = cart_item.cart
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
       
        cart_item.quantity += 1
        cart_item.save()
    except:
        pass
    return JsonResponse({
        "message" : "Item  quantity increased",
        "status" : "success",
    })

def reduce_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
            cart = cart_item.cart
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
    return JsonResponse({
        "message" : "Item  quantity reduced",
        "status" : "success",
    })

def remove_cart_item(request,product_id,cart_item_id):
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user,id=cart_item_id)
        cart = cart_item.cart
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    cart_item_count = cart.cart_products.count()
    if cart_item_count==0:
        cart.delete()
    return redirect('cart')

@login_required(login_url = login)
def checkout(request,cart_id,sub_total=0,quantity=0,coupon_discount=0,cart_items=None,selected_coupon=None):
    current_url = request.get_full_path()
    request.session['current_url'] = current_url
    
    try:
        cart = Cart.objects.get(user=request.user,is_purchased=False)
    except Cart.DoesNotExist:
        messages.info(request,'Items purchased from another browser or device, check order history')
        return redirect('my_orders')

    #response from coupoun modal in checkout page
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon_code = data.get('couponCode')
        selected_coupon = Coupon.objects.get(coupon_code=coupon_code)
        try:
            coupon_usage = CouponHistory.objects.get(user=request.user,is_used=False)
            coupon_usage.cart = cart
            coupon_usage.coupon=selected_coupon
            coupon_usage.save()
        except CouponHistory.DoesNotExist:
            coupon_usage = CouponHistory.objects.create(user=request.user, cart=cart, coupon=selected_coupon,is_used=False)
        selected_coupon = coupon_usage.coupon
        coupon_discount =  selected_coupon.coupon_discount
    else:
        try:
            coupon_history_recent = CouponHistory.objects.get(user=request.user,is_used=False,cart=cart)
            selected_coupon = coupon_history_recent.coupon
            coupon_discount =  selected_coupon.coupon_discount
        except:
            coupon_discount = 0
            selected_coupon = Coupon.objects.get(coupon_discount=coupon_discount)
            coupon_history_recent = CouponHistory.objects.create(user=request.user,is_used=False,cart=cart,coupon=selected_coupon)

    current_user = request.user
    user_addresses = UserAddresses.objects.filter(user=current_user)
    try:
        tax=0
        grand_total=0
        cart_items = CartItem.objects.filter(user=current_user,is_active=True)
        for cart_item in cart_items:
            sub_total += (cart_item.d_item_price*cart_item.quantity)
            quantity += cart_item.quantity
        net_total = round(sub_total*(1-coupon_discount/100),2)
        tax = round(net_total*(2/100),2)
        grand_total = net_total + tax
        
            
    except Cart.DoesNotExist:
        total = quantity = cart_items = None
   
    coupons = Coupon.objects.all()
    coupon_history = CouponHistory.objects.filter(user= current_user)
    if coupon_history.exists():
       used_codes = CouponHistory.objects.values_list('coupon__coupon_code',flat=True)
       coupons = coupons.exclude(coupon_code__in=used_codes)
        
    context = {
            'sub_total' : sub_total,
            'quantity' : quantity,
            'cart_items' : cart_items,
            'tax' : tax,
            'grand_total' : grand_total,
            'user_addresses':user_addresses,
            'coupons':coupons,
            'net_total':net_total,
            'coupon_discount':coupon_discount,
            'discount_amount' : sub_total*coupon_discount/100,
            'cart':cart,
        }    
    
    if request.method == 'POST':
        net_total = sub_total * (1 - coupon_discount / 100)
        return JsonResponse({
            "success" : True,
            "discount" : coupon_discount,
            "discount_amount" : sub_total*coupon_discount/100,
            "net_total" :  net_total,
            "tax" : tax,
            "grand_total" : grand_total,
        })
    return render(request,'store/checkout.html',context)
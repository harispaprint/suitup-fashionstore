import datetime
from django.shortcuts import render,redirect
from accounts.models import UserAddresses
from orders.models import Order, OrderProduct
from store.models import Product,Variation
# from .forms import OrderForm
from carts.models import CartItem
from django.contrib import messages

# Create your views here.
def place_order(request,total=0,quantity=0,order=None):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count<=0:
        return redirect('store')
    
    tax=0
    grand_total=0
    for cart_item in cart_items:
        total += (cart_item.product.price*cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total + tax    
        
    if request.method == 'POST':
        selected_address_id = request.POST.get('address_id',None)
        if selected_address_id:
            selected_address = UserAddresses.objects.get(user=current_user,id=selected_address_id)
            order = Order()
            order.user = current_user
            order.order_address=selected_address
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()  # Save the order to the database

    # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.status = 'Completed'
            order.save()

    context ={
        'order' : order,
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
       
    }

    messages.success(request, f"Order placed successfully! Your order number is {order_number}.")
    return render(request,'orders/payment.html',context)  # Replace 'store' with a success page if needed        

    return redirect('store')

def payment(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    order = Order.objects.get(user=current_user,is_ordered = False)
    print(order)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.user_id = current_user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        #set product variations for ordered products
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=order_product.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce product stock for ordered products
        product = Product.objects.get(id=item.product_id)
        product.stock -=item.quantity
        product.save()
    

    order.is_ordered = True
    order.save()  

    #Remove the products from cart after order complete
    CartItem.objects.filter(user=request.user).delete()

    #contents to invoice
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    subtotal = 0
    for i in ordered_products:
        subtotal += i.product_price * i.quantity
    
    context = {
            'order': order,
            'ordered_products': ordered_products,
            # 'order_number': order.order_number,
            'subtotal': subtotal,
        }
   
    print(subtotal)

    return render(request,'orders/order_successful.html',context)

def cancel_order_page(request,order_id):
    order =Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)
    context = {
            'order': order,
            'ordered_products': ordered_products,
        }
    return render(request,'orders/cancel_order_page.html',context)

def cancel_order(request,order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    return redirect('my_orders')

def cancel_ordered_product(request,ordered_product_id):
    ordered_product = OrderProduct.objects.get(id=ordered_product_id)
    order = ordered_product.order
    ordered_product.delete()
    ordered_products = OrderProduct.objects.filter(order=order)
    context = {
            'order': order,
            'ordered_products': ordered_products,
        }
    return render(request,'orders/cancel_order_page.html',context)
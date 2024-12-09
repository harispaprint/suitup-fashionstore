import datetime
from django.shortcuts import render,redirect
from orders.models import Order, OrderProduct
from store.models import Product,Variation
from .forms import OrderForm
from carts.models import CartItem
from django.contrib import messages

# Create your views here.
def place_order(request,total=0,quantity=0):
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
        
    # return render(request,'orders/place_order.html')

    if request.method == 'POST':
        print('Entered form')
        form = OrderForm(request.POST)
        if form.is_valid():
            print('form is valid')
            # Create an instance without saving to the database yet
            order = Order()
            order.user = current_user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address_line_1 = form.cleaned_data['address_line_1']
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.city = form.cleaned_data['city']
            order.state = form.cleaned_data['state']
            order.country = form.cleaned_data['country']
            order.order_note = form.cleaned_data['order_note']
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()  # Save the order to the database
            print('saved order')

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(order.id)
            order.order_number = order_number
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
        else:
            messages.error(request, "There was an error in your form. Please check the details.")
      
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
    


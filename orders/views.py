import datetime
from django.shortcuts import render,redirect
from orders.models import Order
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

            messages.success(request, f"Order placed successfully! Your order number is {order_number}.")
            return redirect('store')  # Replace 'store' with a success page if needed
        else:
            messages.error(request, "There was an error in your form. Please check the details.")
      
    return redirect('store')
    


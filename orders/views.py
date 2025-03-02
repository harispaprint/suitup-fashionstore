from time import timezone
from venv import logger
from django.http import HttpResponse, JsonResponse
import razorpay # type: ignore
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import get_object_or_404, render,redirect
from accounts.models import UserAddresses
from orders.models import CancelProduct, CouponHistory, Order, OrderProduct, Payment, ReturnProduct, Wallet, WalletTransaction
from store.models import Coupon, Product,Variation
# from .forms import OrderForm
from carts.models import Cart, CartItem
from django.contrib import messages
import json
import logging
from django.db.models import Q,Count
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.template.loader import render_to_string
from weasyprint import HTML




# Create your views here.
@login_required(login_url='login')
def my_orders(request, status=None):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if status == 'pending':
        orders = orders.filter(payment_mode='pay_now').annotate(status_count=Count('payment_order', filter=Q(payment_order__payment_status__iexact='cancelled')))
    elif status!='all':
        orders = orders.annotate(status_count=Count('order_products', filter=Q(order_products__status__iexact=status)))
    else:
        orders = orders.annotate(status_count=Count('order_products'))
    context = {
        'orders': orders,
        'status': status,
    }
    return render(request, 'orders/my_orders.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    current_user = request.user
    order_user = order.user
    if request.user == order.user or request.user.is_admin:
        for i in order_detail:
            subtotal += i.product_price * i.quantity

        context = {
            'order_detail': order_detail,
            'order': order,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_detail.html', context)
    else:
        return redirect('store')

def place_order(request,sub_total=0,quantity=0,order=None,coupon_selected=None,coupon_discount=0):  
    wallet_amount=0
    wallet=None
    current_user = request.user
    if request.method == 'POST':
        if request.POST.get('form') == 'walletform':
            wallet_amount = float(request.POST.get('wallet_amount'))
            
            order = Order.objects.filter(user=current_user).latest('created_at')
    try:        
        wallet = Wallet.objects.get(user=current_user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=current_user)
    try:
        cart = Cart.objects.get(user=request.user,is_purchased=False)
    except Cart.DoesNotExist:
            messages.info(request,'Items purchased from another browser or device, check order history')
            return redirect('my_orders')
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    try:
        coupon_history_recent = CouponHistory.objects.get(user=current_user,cart=cart,is_used=False)
        coupon_selected = coupon_history_recent.coupon
        # print(f"coupon selected : {coupon_selected}")
        coupon_discount = coupon_selected.coupon_discount
        # print(f"coupon discount : {coupon_discount}")
    except:
        pass

    if cart_count<=0:
        return redirect('store')
    
    tax=0
    grand_total=0
    for cart_item in cart_items:
        sub_total += (cart_item.d_item_price*cart_item.quantity)
        quantity += cart_item.quantity
    net_total = round(sub_total*(1-coupon_discount/100),2)
    tax = round((2*net_total)/100,2)
    grand_total = round(net_total + tax,0)
    payable_amount=grand_total-wallet_amount
    
    #update grand total in order object is wallet amount is used
    if order is not None:
        order.payable_amount = payable_amount
        order.wallet_amount_used = wallet_amount
        order.save()
        
        
    if request.method == 'POST':
        if request.POST.get('form') == 'checkoutform':
            selected_address_id = request.POST.get('address_id',None)
            if selected_address_id:
                selected_address = UserAddresses.objects.get(user=current_user,id=selected_address_id)

                #checking whether any previous order object by the user is incomplete.
                #This is to avoid creation of new order object on page reload
                is_incomplete_order = Order.objects.filter(user=current_user,status='new').exists()
                if is_incomplete_order:
                    order = Order.objects.filter(user=current_user,status='new').first()
                else:
                    order = Order()
                order.user = current_user
                order.order_address=selected_address
                order.sub_order_total = sub_total
                order.net_order_total = net_total
                order.grand_order_total = grand_total
                order.payable_amount = grand_total #initially same as grand total, if wallet is used, changes.
                order.coupon = coupon_selected
                order.tax = tax
                order.ip = request.META.get('REMOTE_ADDR')
                order.status = 'new'
                order.save()  # Save the order to the database

    # Generate order number
            order_number = datetime.now().strftime("%Y%m%d") + str(order.id)
            order.order_number = order_number
            
            order.save()

    context ={
        'order' : order,
        'sub_total' : sub_total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'net_total':net_total,
        'coupon_discount':coupon_discount,
        'discount_amount' : sub_total*coupon_discount/100,
        'wallet':wallet,
        'wallet_amount':wallet_amount,
        'payable_amount':payable_amount,
    }

    # messages.success(request, f"Order placed successfully! Your order number is {order_number}.")
    return render(request,'orders/place_order.html',context)  # Replace 'store' with a success page if needed        

    return redirect('store')

def check_coupon(request):
    if request.method == "POST":
        data = json.loads(request.body)
        coupon_code = data.get("couponCode")
        print(coupon_code)

        # Simulate checking coupon in the database
        
        coupon_used = CouponHistory.objects.filter(user=request.user,coupon__coupon_code=coupon_code,is_used=True).exists()
        

        if coupon_code == 'No Discount':
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            return JsonResponse({"isValid": True, "discount": coupon.coupon_discount})
        elif not coupon_used:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            return JsonResponse({"isValid": True, "discount": coupon.coupon_discount})
        else:
            return JsonResponse({"isValid": False})
    return JsonResponse({"error": "Invalid request"}, status=400)


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment(request,order_id):
    current_user = request.user
    try:
        cart = Cart.objects.get(user=request.user,is_purchased=False)
    except Cart.DoesNotExist:
        messages.info(request,'Items purchased from another browser or device, check order history')
        return redirect('my_orders')
    cart_items = CartItem.objects.filter(user=current_user)
    order_server = Order.objects.get(id=order_id)
    for item in cart_items:
        try:
            order_product = OrderProduct.objects.get(order_id=order_server.id,product_id=item.product_id,stock = item.stock,status='new')
        except:
            order_product = OrderProduct()
        order_product.order_id = order_server.id
        order_product.user_id = current_user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity

        order_product.stock = item.stock
        
        coupon_discount = order_server.coupon.coupon_discount
        order_product.product_price = round(item.d_item_price*(1-coupon_discount/100),2)
        
        order_product.ordered = True
        order_product.save()

    if order_server.payable_amount == 0:
        order_server.payment_mode = 'wallet'
        order_server.save()
        invoice_url = f"/orders/invoice/{order_server.id}/"
        return redirect(invoice_url)

    elif request.method == "POST":
        payment_method = request.POST.get("payment_method")


        if payment_method == "pay_now":
            order_data = {
            'amount': int(order_server.payable_amount * 100), 
            'currency': 'INR',
            'payment_capture': '1'
            }
               
            order = client.order.create(data=order_data)
            payment = Payment.objects.create(user=request.user,
                                             order=order_server,
                                             razorpay_order_id=order["id"],
                                             amount_paid=order_server.payable_amount)

            
            # order_server.razorpay_order_id=order["id"]
            order_server.payment_mode = payment_method
            order_server.save()
            # amount=order_server.net_order_total
            
            context = {
                'order_id': order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id_server': order_server.id,
                'price': order_server.payable_amount,
                }
            return render(request,'orders/payment.html',context)
        

        elif payment_method == "cash_on_delivery":
            order_server.payment_mode = payment_method
            order_server.save()
            invoice_url = f"/orders/invoice/{order_server.id}/"
            return redirect(invoice_url)


    #Remove the products from cart after order complete
    # CartItem.objects.filter(user=request.user).delete()

    # #contents to invoice
    # ordered_products = OrderProduct.objects.filter(order_id=order.id)
    # subtotal = 0
    # for i in ordered_products:
    #     subtotal += i.product_price * i.quantity
    
    # context = {
    #         'order': order,
    #         'ordered_products': ordered_products,
    #         # 'order_number': order.order_number,
    #         'subtotal': subtotal,
    #     }
   

    # return render(request,'orders/order_successful.html',context)


logger = logging.getLogger(__name__)

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        try:
            payment_response = json.loads(request.body)
            
            params_dict = {
                'razorpay_order_id': payment_response.get('razorpay_order_id'),
                'razorpay_payment_id': payment_response.get('razorpay_payment_id'),
                'razorpay_signature': payment_response.get('razorpay_signature')
            }

            # Ensure all fields are present
            if not all(params_dict.values()):
                logger.error(f"Incomplete payment details received: {params_dict}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Incomplete payment details'
                }, status=400)

            try:
                # Verify the payment signature
                client.utility.verify_payment_signature(params_dict)

                # Fetch and update payment record
                try:
                    payment = Payment.objects.get(razorpay_order_id=params_dict['razorpay_order_id'])
                    
                    if payment.payment_verified:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Payment was already verified'
                        })

                    payment.razorpay_payment_id = params_dict['razorpay_payment_id']
                    payment.payment_verified = True
                    payment.payment_status = 'success'
                    payment.verified_at = datetime.now()
                    payment.save()

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Payment verified successfully'
                    })

                except Payment.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Payment record not found'
                    }, status=404)

            except Exception as e:
                logger.error(f"Signature verification failed: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Payment verification failed'
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON payload'
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

def invoice(request,order_id):
    current_user = request.user
    order_server = Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order_id=order_id)
    for item in ordered_products:
        item.stock.product_stock -= item.quantity
        item.stock.save()
    
    discount_amount = order_server.sub_order_total*order_server.coupon.coupon_discount/100
  
    context = {
            'order': order_server,
            'ordered_products': ordered_products,
            'discount_amount':discount_amount,
        }
    print(order_server)
    print(ordered_products)

    order_server.is_ordered = True
    order_server.status = 'confirmed'
    ordered_products.update(status='confirmed')
    order_server.save()
    wallet_amount_used = order_server.wallet_amount_used
    if wallet_amount_used > 0:
        wallet = Wallet.objects.get(user=current_user)
        wallet.wallet_balance -= wallet_amount_used
        wallet.save() 
        wallet_transaction= WalletTransaction.objects.create(wallet=wallet,transaction_amount=wallet_amount_used,order=order_server,transaction_type='purchase')


    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items.exists():
        cart = cart_items.first().cart
        try:
            coupon_history = CouponHistory.objects.get(cart=cart)
            coupon_history.is_used = True
            coupon_history.save()
        except:
            pass
        cart.is_purchased=True
        cart.save()
    cart_items.delete()
   
    # return render(request,'orders/invoice_pdf.html',context)
    return render(request,'orders/invoice.html',context)

def payment_cancelled(request,order_id):
    order_server = Order.objects.get(id=order_id)
    try:
        payment = Payment.objects.get(order=order_server, payment_status='pending')
    except:
        payment = Payment.objects.filter(order=order_server).order_by('-created_at').first()
    payment.payment_status = 'cancelled'
    payment.failure_reason = 'modal closed'
    order_server.save()
    payment.save()

    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items.exists():
        cart = cart_items.first().cart
        coupon_history = CouponHistory.objects.get(cart=cart)
        coupon_history.is_used = True
        coupon_history.save()
        cart.is_purchased=True
        cart.save()
    cart_items.delete()
    return render(request,'orders/payment_cancelled.html')

def retry_failed_payment(request,order_id):
    order_server = Order.objects.get(id=order_id)
    print(order_server)
    payment = Payment.objects.filter(order=order_server,payment_status='cancelled').first()

    if payment.payment_status == "cancelled":
        order_data = {
            'amount': int(order_server.payable_amount * 100),
            'currency': 'INR',
            'payment_capture': '1'
            }
        new_order = client.order.create(data=order_data)
        
        # Update payment record
        payment.razorpay_order_id = new_order["id"]
        payment.status = "pending"
    
        context = {
                    'order_id': new_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'order_id_server': order_server.id,
                    'price': payment.amount_paid,
                    }
        return render(request,'orders/payment.html',context)

def payment_status(request, order_id):
    try:
        order = Order.objects.get(payment__razorpay_order_id=order_id)
        if order.payment_verified:
            # set product variations for ordered products
            # cart_item = CartItem.objects.get(id=item.id)
            # orderproduct = OrderProduct.objects.get(id=order_product.id)
            # order_product.stock = cart_item.stock
            # orderproduct.save()
            # orderproduct.stock.product_stock-=order_product.quantity
            # orderproduct.stock.save()
            # order.is_ordered = True
            # order.save()  
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failed'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Order not found'})

def ordered_product_status(request,order_product_id,wallet=None):
    url = request.META.get('HTTP_REFERER')
    order_product = OrderProduct.objects.get(id=order_product_id)
    order = order_product.order
    if request.method == "POST":
        action = request.POST.get('change_status')

        # Handle form submission based on the selected action
        if action == 'cancel':
            order_product.status = 'cancelled'
            order_product.save()
            count_cancelled = order.order_products.filter(status__iexact='cancelled').count()
            total_product_count = order.order_products.all().count()
            if total_product_count-count_cancelled>0:
                order.status = "Partially Cancelled"
                order.save()
            elif total_product_count-count_cancelled==0:
                order.status = "Fully Cancelled"
                order.save()
        elif action == 'return':
            order_product.status = 'return_request'
            order_product.save()
    return redirect(url)

def product_cancel_request(request,order_product_id):
    if request.method=='POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        order_product = OrderProduct.objects.get(id=order_product_id)
        CancelProduct.objects.create(order_product=order_product,reason=reason,description=description,status='initiated')
        order_product.status = 'cancelled'
        order_product.save()
    return redirect('my_orders')

def product_return_request(request,order_product_id):
    if request.method=='POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        order_product = OrderProduct.objects.get(id=order_product_id)
        ReturnProduct.objects.create(order_product=order_product,reason=reason,description=description,status='initiated')
        order_product.status = 'return_requested'
        order_product.save()
    return redirect('my_orders')

def order_product_refund(request,order_product_id):
    url = request.META.get('HTTP_REFERER')
    order_product = get_object_or_404(OrderProduct, id=order_product_id)
    order = order_product.order
    refund_amount = order_product.total_price()
    transaction_type = 'refund'
    order.refunded_amount += refund_amount
    order.current_order_total-=refund_amount
    order.save()
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user)
    wallet.update_balance(transaction_type,refund_amount)
    wallet_transaction = WalletTransaction.objects.create(wallet=wallet,transaction_amount=refund_amount,order=order,order_product=order_product,transaction_type=transaction_type)

    return_product = ReturnProduct.objects.get(order_product=order_product)
    return_product.status = 'refund_completed'
    return_product.save()

    return redirect(url)

def generate_invoice_pdf(request,order_id):
    order=None
    # order_id = request.POST.get('order', None)  # Gets order as a string
    # if order_id:
    #     try:
    #         order = Order.objects.get(id=int(order_id))  # Convert and fetch object
    #         print(order.id)  # Now this works!
    #     except Order.DoesNotExist:
    #         print("Order not found")
    # else:
    #     print("No order ID provided")
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        print("Order not found")
    ordered_products = OrderProduct.objects.filter(order_id=int(order_id))
    print(ordered_products)
    invoice_data = {
        'order':order,
        'ordered_products':ordered_products,
    }

    
    invoice_data['logo_url']=request.build_absolute_uri(static('images/suitup_logo.png'))
    invoice_data['bootstrap_url']=request.build_absolute_uri(static('css/bootstrap.css'))
    
    
    html_content = render_to_string('orders/invoice_pdf.html',invoice_data)

    # Generate the PDF
    pdf = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    # Return the response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=f"order_{order.id}.pdf"'  # Change to 'inline' for in-browser view
    return response

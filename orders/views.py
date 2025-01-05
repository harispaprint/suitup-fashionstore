from time import timezone
from venv import logger
from django.http import HttpResponse, JsonResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render,redirect
from accounts.models import UserAddresses
from orders.models import Order, OrderProduct, Payment
from store.models import Product,Variation
# from .forms import OrderForm
from carts.models import CartItem
from django.contrib import messages
import json
import logging




client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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
        total += (cart_item.stock.price*cart_item.quantity)
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
            order_number = datetime.now().strftime("%Y%m%d") + str(order.id)
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
    return render(request,'orders/place_order.html',context)  # Replace 'store' with a success page if needed        

    return redirect('store')

def payment(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    order_server = Order.objects.get(user=current_user,is_ordered = False)

    # print(order)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order_server.id
        order_product.user_id = current_user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.stock.price
        order_product.ordered = True
        order_product.save()

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "pay_now":
            order_data = {
            'amount': int(order_server.order_total * 100), 
            'currency': 'INR',
            'payment_capture': '1'
            }
               
            order = client.order.create(data=order_data)
            payment = Payment.objects.create(user=request.user,razorpay_order_id=order["id"],amount_paid=order_server.order_total)
            
            # order_server.razorpay_order_id=order["id"]
            order_server.payment_mode = payment_method
            order_server.payment=payment
            order_server.save()
            amount=order_server.order_total
            
            context = {
                'order_id': order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id_server': order_server.id,
                'price': order_server.order_total,
                }
            return render(request,'orders/payment.html',context)
        

        elif payment_method == "cash_on_delivery":
            order_server.payment_mode = payment_method
            return redirect('invoice') 

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
   
    # print(subtotal)

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

def invoice(request):
    current_user = request.user
    order_server = Order.objects.get(user=current_user,is_ordered = False)
    ordered_products = OrderProduct.objects.filter(order_id=order_server.id)
    subtotal = 0
    for i in ordered_products:
        subtotal += i.product_price * i.quantity
    context = {
            'order': order_server,
            'ordered_products': ordered_products,
            # 'order_number': order.order_number,
            'subtotal': subtotal,
        }
    order_server.is_ordered = True
    order_server.save()
    CartItem.objects.filter(user=request.user).delete()
    return render(request,'orders/invoice.html',context)


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




# def process_successful_payment(payment):
#     """
#     Handles critical backend operations after payment verification
#     """
#     try:
#         # 1. Update Order Status
#         order = payment.order  # Assuming there's a related Order model
#         order.status = 'paid'
#         order.paid_at = timezone.now()
#         order.save()

#         # 2. Send confirmation email to customer
#         send_mail(
#             subject=f'Order Confirmation #{order.id}',
#             message=f'Thank you for your payment of ₹{payment.amount/100:.2f}',
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[order.email],
#             fail_silently=True,
#         )

#         # 3. Update Inventory
#         for item in order.items.all():  # Assuming there's a related Items model
#             product = item.product
#             product.stock -= item.quantity
#             product.save()

#         # 4. Create Invoice
#         invoice = Invoice.objects.create(
#             order=order,
#             payment=payment,
#             amount=payment.amount,
#             generated_at=timezone.now()
#         )

#         # 5. Notify Admin/Staff
#         send_mail(
#             subject=f'New Order #{order.id}',
#             message=f'New order received and payment verified.',
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[settings.ADMIN_EMAIL],
#             fail_silently=True,
#         )

#         # 6. Record Analytics
#         record_sale_analytics(order)

#     except Exception as e:
#         logger.error(f"Error in post-payment processing for payment {payment.id}: {str(e)}")
#         # Don't raise the exception - we don't want to roll back the payment verification
#         # just because post-processing failed
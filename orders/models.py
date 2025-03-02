from django.db import models
from carts.models import Cart
from accounts.models import Account,UserAddresses
from store.models import Coupon, Product, Stock,Variation
from decimal import Decimal


# # Create your models here.
# class Payment(models.Model):
#     user = models.ForeignKey(Account, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order,on_delete=models.CASCADE)
#     razorpay_order_id = models.CharField(max_length=100, unique=True)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     amount_paid = models.CharField(max_length=100) # this is the total amount paid
#     payment_verified = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     payment_status = models.CharField(max_length=20, default='pending')
#     failure_reason = models.CharField(max_length=100, null=True, blank=True)
#     verified_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.razorpay_order_id


class Order(models.Model):
    STATUS = (
        ('Confirmed','confirmed'),
        ('Shipped','shipped'),
        ('Delivered','delivered'),
        ('Cancelled','cancelled'),
        ('Return','return'),
    )

    PAYMENT_MODES = (
        ('Cash on Delivery','cash_on_delivery'),
        ('Pay Now','pay_ow'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment_mode = models.CharField(max_length=200,choices=PAYMENT_MODES, default='cash_on_delivery')
    # payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    order_address = models.ForeignKey(UserAddresses,on_delete=models.SET_NULL,null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    sub_order_total = models.FloatField()
    net_order_total = models.FloatField()
    tax = models.FloatField()
    grand_order_total = models.FloatField()
    wallet_amount_used = models.FloatField(default=0.0)
    payable_amount = models.FloatField(default=0.0)
    refunded_amount = models.FloatField(default=0.0)
    current_order_total = models.FloatField(default=0.0)
    status = models.CharField(max_length=50, choices=STATUS, default='confirmed')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.order_number
    
    

class OrderProduct(models.Model):
    STATUS = (
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('returned','Returned'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_products')
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="product_ordered")
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    status = models.CharField(max_length=50,choices=STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['id']  # Ascending order by id

    def p_discount_price(self):
        p_discount_price = self.stock.discounted_price(self.quantity)*self.quantity
        return p_discount_price
    
    def total_price(self):
        total = round(self.quantity*self.product_price,2)
        return total


    def __str__(self):
        return self.product.product_name
    
class CouponHistory(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.SET_NULL,null=True,related_name='cart_coupon')
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE)
    availed_date = models.DateTimeField(auto_now=True)
    # is_current_session = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.coupon}"
    
class Wallet(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    wallet_balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - wallet"
    
    def update_balance(self,transaction_type,amount):
        amount = float(amount)
        if transaction_type.lower() in {'refund','add_cash'}:
            self.wallet_balance += amount
        elif transaction_type.lower() in {'purchase','transfer'}:
            self.wallet_balance -= amount
        self.save()
    
class WalletTransaction(models.Model):
    CHOICES = [
        ('refund','Refund'),
        ('purchase','Purchase'),
        ('add_cash','Add Cash'),
        ('transfer','Transfer'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE,related_name='transaction_wallet')
    transaction_amount = models.FloatField()
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_wallet',null=True,blank=True)
    order_product = models.ForeignKey(OrderProduct,on_delete=models.CASCADE,related_name='order_product_wallet',null=True,blank=True)
    transaction_type = models.CharField(max_length=50,choices=CHOICES)
    transaction_description = models.TextField(max_length=250,null=True,blank=True)
    transaction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet} - {self.transaction_type} - {self.transaction_amount}"
    
class ReturnProduct(models.Model):
    REASON_CHOICES = [
        ('damaged', 'Damaged or Defective Product'),
        ('wrong_product', 'Wrong Product Delivered'),
        ('size_issue', 'Size or Fit Issues'),
        ('not_as_described', 'Product Not as Described'),
        ('missing_items', 'Missing Items'),
        ('quality_issue', 'Quality Issues'),
        ('performance_issue', 'Performance Issues'),
        ('expired_product', 'Expired Product'),
        ('change_of_mind', 'Change of Mind'),
        ('better_price', 'Better Price Available'),
        ('tampered_package', 'Package Tampered'),
    ]
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('refund_completed', 'Refund Completed'),
    ]
    order_product = models.ForeignKey(OrderProduct,on_delete=models.CASCADE,related_name='order_return')
    reason = models.CharField(max_length=100,choices=REASON_CHOICES)
    description = models.TextField(null=True,blank=True)
    refund_ammount = models.FloatField(default=0.0)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_product.product} - {self.reason}"
    
class CancelProduct(models.Model):
    order_product = models.ForeignKey(OrderProduct,on_delete=models.CASCADE,related_name='order_cancel')
    reason = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    refund_amount = models.FloatField(default=0.0)
    status = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_product.product} - {self.reason}"

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="payment_order",null=True,blank=True)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.CharField(max_length=100) # this is the total amount paid
    payment_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='pending')
    failure_reason = models.CharField(max_length=100, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.razorpay_order_id




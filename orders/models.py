from django.db import models
from accounts.models import Account,UserAddresses
from store.models import Product, Stock,Variation


# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
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


class Order(models.Model):
    STATUS = (
        ('Confiremd','confiremd'),
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
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    order_address = models.ForeignKey(UserAddresses,on_delete=models.SET_NULL,null=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='confirmed')
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name




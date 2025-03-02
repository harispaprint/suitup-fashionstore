from django.db import models
from store.models import Product, Stock,Variation
from accounts.models import Account

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250,blank=True)
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_purchased = models.BooleanField(default=False)
    # is_non_user_cart = models.BooleanField(default=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.SET_NULL,null=True,related_name='cart_products')
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    discount = models.FloatField(default=0)
    d_item_price = models.FloatField(default=0)
    savings = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']  # Ascending order by id


    def sub_total(self):
        return self.stock.price*self.quantity
    
    def sub_total_discount(self):
        return self.d_item_price*self.quantity

    def __unicode__(self):
        return self.product
    
class CartOffer(models.Model):
    offer_name = models.CharField(max_length=100)
    min_amount = models.IntegerField()
    discount = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.offer_name}" 
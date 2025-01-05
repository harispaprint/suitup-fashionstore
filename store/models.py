from django.db import models
from django.urls import reverse
from accounts.models import Account
from category.models import Category
from django.db.models import Avg,Count

# Create your models here.
class Product(models.Model):
    product_name    = models.CharField(max_length=200,unique=True)
    slug            = models.SlugField(max_length=200,unique=True)
    description     = models.TextField(max_length=500,blank=True)
    price           = models.IntegerField()
    images          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])
    
    def avg_rating(self):
        ratings = ReviewsRatings.objects.filter(product=self,review_active=True).aggregate(average=Avg('rating'))
        avg=0
        if ratings['average'] is not None:
            avg = float(ratings['average'])
        return avg
    
    def count_reviews(self):
        reviews = ReviewsRatings.objects.filter(product=self,review_active=True).aggregate(count=Count('id'))
        count=0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def __str__(self):
        return self.product_name
    
class ProductImage(models.Model):
        product = models.ForeignKey(Product, related_name="product_images", on_delete=models.CASCADE)
        image = models.ImageField(upload_to='photos/products')

        def __str__(self):
            return f"Image for {self.product.product_name}"


class VariationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.ForeignKey(VariationCategory, on_delete=models.CASCADE)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.product_name}-{self.variation_category.name}-{self.variation_value}"


class Stock(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='stock_product',null=True)
    variation_combo = models.ManyToManyField(Variation,related_name='product_variation_combo')
    product_stock = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    search_key = models.CharField(max_length=255,null=True,blank=True)

    def variation_info(self):
        variations = ", ".join([str(variation.variation_category.name)+":"+str(variation.variation_value)  for variation in self.variation_combo.all()])
        return f"{variations}"

    def discounted_price(self,item_qty):
        try:
            offer = BulkPurchaseOffer.objects.filter(product=self.product).first()
            print(offer)
            if item_qty>=offer.min_qty:
                d_price = self.price*(1-offer.current_discount(item_qty)/100)
            else:
                d_price = self.price
        except BulkPurchaseOffer.DoesNotExist:
            d_price = self.price
        return d_price

    def __str__(self):
        variations = ", ".join(str(variation.variation_category.name)+":"+str(variation.variation_value) for variation in self.variation_combo.all())
        return f"{self.product.product_name} - {variations}"
    
class ReviewsRatings(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    review_subject = models.CharField(max_length=250)
    review_body = models.TextField(null=True,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=30,blank=True)
    review_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.user.username}"
    
class Coupon(models.Model):
    coupon_code = models.CharField(max_length=100)
    coupon_description = models.TextField(null=True,blank=True)
    coupon_discount = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.coupon_code

class BulkPurchaseOffer(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='bulk_offer_product')
    offer_name = models.CharField(max_length=100)
    min_qty = models.IntegerField()
    fixed_discount = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    is_fixed = models.BooleanField(default=True)

    def current_discount(self,item_qty):
        if not self.is_fixed:
            c_discount = (item_qty//self.min_qty)*self.fixed_discount
        else:
            c_discount = self.fixed_discount
        return c_discount

    def __str__(self):
        return f"{self.offer_name} - {self.product.product_name}"

    
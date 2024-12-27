from django.db import models
from django.urls import reverse
from category.models import Category

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
        return f"{self.variation_category.name}: {self.variation_value}"


class Stock(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='stock_product',null=True)
    variation_combo = models.ManyToManyField(Variation,related_name='product_variation_combo')
    product_stock = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    search_key = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        variations = ", ".join([str(variation) for variation in self.variation_combo.all()])
        return f"{self.product.product_name} - {variations}"
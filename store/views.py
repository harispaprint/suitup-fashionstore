from django.shortcuts import render,get_object_or_404,redirect
from store.models import Product,ProductImage
from category.models import Category
from .forms import AddProductForm
from django.contrib import messages
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.
def store(request,category_slug=None):
    categories = None
    products = None
    sort = request.GET.get('sort', 'product_name')  
    if category_slug!=None:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.all().filter(category=categories,is_available=True).order_by(sort)
        products_count = products.count()
    
    else:
        products = Product.objects.all().filter(is_available=True).order_by(sort)
        products_count = products.count()
    
    context = {
       'products':products,
       'products_count':products_count
      }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        additional_images = ProductImage.objects.filter(product=single_product)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()
        
    except Exception as e:
        raise e
    
    context = {
            'single_product':single_product,
            'additional_images':additional_images,
            'in_cart':in_cart
        }
     
    return render(request,'store/product_detail.html',context)




def delete_product(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    product.delete()
    print('product deleted')
    return redirect('product_management')


def add_product(request):
    if request.method == 'POST':
        product_add_form = AddProductForm(request.POST, request.FILES)
        if product_add_form.is_valid():
            product_add_form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')  # Redirect to a product listing page or another page
        else:
            messages.error(request, 'Failed to add product. Please correct the errors below.')
    else:
        product_add_form = AddProductForm()

    context = {
        'product_add_form': product_add_form
    }
    print(context)
    return render(request, 'myadmin/add_product.html', context)

def search(request):
    products = []
    products_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword.strip():  # Ensure the keyword is not empty or only whitespace
            # Apply filtering logic using Q object
            products = Product.objects.filter(
                Q(product_name__icontains=keyword) | Q(description__icontains=keyword)
            )
            products_count = products.count()
    
    context = {
        'products': products,
        'products_count': products_count  # Corrected the variable name
    }
    return render(request, 'store/store.html', context)

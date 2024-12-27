from django.shortcuts import render,get_object_or_404,redirect
from store.utils import get_product_stock
from store.models import Product,ProductImage, Variation
from category.models import Category
from .forms import AddProductForm
from django.contrib import messages
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.db.models import Q
from django.http import JsonResponse

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

# def product_detail(request,category_slug,product_slug):
#     try:
#         single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
#         additional_images = ProductImage.objects.filter(product=single_product)
#         in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()
        
#     except Exception as e:
#         raise e
    
#     context = {
#             'single_product':single_product,
#             'additional_images':additional_images,
#             'in_cart':in_cart
#         }
     
#     return render(request,'store/product_detail.html',context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        additional_images = ProductImage.objects.filter(product=single_product)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

        # Fetch variations for the product
        variations = Variation.objects.filter(product=single_product, is_active=True)

        # Group variations by category
        grouped_variations = {}
        for variation in variations:
            category = variation.variation_category.name  # Assuming you use VariationCategory as a foreign key
            if category not in grouped_variations:
                grouped_variations[category] = []
            grouped_variations[category].append(variation.variation_value)

    except Product.DoesNotExist:
        # Handle product not found
        return redirect('store')  # Redirect to a relevant page or show an error page
    
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'additional_images': additional_images,
        'in_cart': in_cart,
        'grouped_variations': grouped_variations,  # Pass grouped variations to the template
    }

    return render(request, 'store/product_detail.html', context)



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

def check_stock(request,product_id):
    stock_count=0
    stock_info = False
    product_price=0
    if request.method == "GET":
        product = Product.objects.get(id=product_id)
        variations = ", ".join([f"{key}: {str(request.GET.get(key))}" for key in request.GET])
        search_key = f"{product.product_name}-{variations}"
        try:
            stock = get_product_stock(search_key)
            print(stock)
            stock_count = stock.product_stock
            product_price = stock.price
            stock_info = True
        except:
            stock_info = False


        in_stock = stock_count > 0

        response_data = {
           "stock_status": f"<h5 class='{ 'text-success' if in_stock else 'text-info' if not stock_info else 'text-danger' }'>"
                         f"{'In Stock (' + str(stock_count) + ' available)' if in_stock else 'Stock info not available' if not stock_info  else 'Out of Stock'}</h5>",
           "can_add_to_cart": in_stock,
           "product_price": f"${product_price}",
           "stock_count": stock_count
       }
        return JsonResponse(response_data)
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from orders.models import Order, OrderProduct
from store.models import Product,ProductImage
from accounts.models import Account
from category.models import Category
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required
from store.forms import AddProductForm, AddVariationForm,ProductImageForm
from category.forms import AddCategoryForm
from django.utils.text import slugify
from .utils import admin_required

def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            if user.is_admin:
                print('Admin')
                auth.login(request,user)
                return redirect('customer_management')
                
            else:
                messages.info(request,'You do not have admin privilege')
                return redirect('admin_login')
        else:
            messages.error(request,'Invalid Credentials')
            return redirect('admin_login')

    return render(request,'myadmin/admin_login.html')


@admin_required
def admin_logout(request):
    auth.logout(request)
    messages.success(request,'Logged Out Successfully')
    return redirect('admin_login')


@admin_required
def customer_management(request):
    users = Account.objects.all()
    context = {
        'users':users
    }
    return render(request,'myadmin/customer_management.html',context)


@admin_required
def product_management(request):
    products = Product.objects.all()
    context = {
        'products':products
    }
    return render(request,'myadmin/product_management.html',context)


@admin_required
def category_management(request):
    categories = Category.objects.all()
    context = {
        'categories':categories
    }
    return render(request,'myadmin/category_management.html',context)

@admin_required
def order_management(request):
    orders = Order.objects.all()
    context = {
        'orders': orders
    }
    return render(request,'myadmin/order_management.html',context)

@admin_required
def admin_cancel_order_page(request,order_id):
    order =Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)
    context = {
            'order': order,
            'ordered_products': ordered_products,
        }
    return render(request,'myadmin/admin_cancel_order_page.html',context)

@admin_required
def admin_cancel_order(request,order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    return redirect('order_management')

@admin_required
def admin_cancel_ordered_product(request,ordered_product_id):
    ordered_product = OrderProduct.objects.get(id=ordered_product_id)
    order = ordered_product.order
    ordered_product.delete()
    ordered_products = OrderProduct.objects.filter(order=order)
    context = {
            'order': order,
            'ordered_products': ordered_products,
        }
    return render(request,'myadmin/admin_cancel_order_page.html',context)



@admin_required
def inventory_management(request):
    products = Product.objects.all()
    context = {
        'products':products
    }
    return render(request,'myadmin/inventory_management.html',context)


@admin_required
def user_status_update(request,user_id):
    user = Account.objects.get(id=user_id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return redirect('customer_management')


@admin_required
def delete_user(request,user_id):
    user = get_object_or_404(Account,id=user_id)
    user.delete()
    print('user deleted')
    return redirect('customer_management')



@admin_required
def add_product(request):
    if request.method == 'POST':
        product_form = AddProductForm(request.POST, request.FILES)
       
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.slug = slugify(product.product_name)
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_management')  
        else:
            print(product_form.errors)
            messages.error(request, 'Failed to add product. Please correct the errors below.')
    else:
        product_form = AddProductForm()

    context = {
        'product_form': product_form
    }
    print(context)
    return render(request, 'myadmin/product_form.html', context)

@admin_required
def add_product_images(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    if request.method=='POST':
        image_form = ProductImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            for img in request.FILES.getlist('image'):
                ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Product added successfully!")
            return redirect('product_management')
    else:
         image_form = ProductImageForm()
    context = {
        'image_form': image_form,
    }
    return render(request,'myadmin/product_image_form.html',context)

@admin_required
def add_product_variation(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    if request.method=='POST':
        variation_form = AddVariationForm(request.POST)
        if variation_form.is_valid():
            variation = variation_form.save(commit=False)
            variation.save()
            messages.success(request, 'Variation added successfully!')
            return redirect('product_management')
    else:
         variation_form = AddVariationForm()
    context = {
        'variation_form': variation_form,
    }
    return render(request,'myadmin/product_variation_form.html',context)

@admin_required
def edit_product(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    if request.method == 'POST':
        product_form = AddProductForm(request.POST,request.FILES,instance=product)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.slug = slugify(product.product_name)
            product.save()
            messages.success(request, 'Product edited successfully!')
            return redirect('product_management')
        else:
            print(product_form.errors)
            messages.error(request, 'Failed to edit product. Please correct the errors below.')
    else:
        product_form = AddProductForm(instance=product)
    context = {
        'product_form':product_form
    }
    return render(request,'myadmin/product_form.html',context)


@admin_required
def product_status_update(request,product_id):
    product = Product.objects.get(id=product_id)
    if product.is_available:
        product.is_available = False
    else:
        product.is_available = True
    product.save()
    return redirect('product_management')


@admin_required
def add_category(request):
    if request.method == 'POST':
        category_add_form = AddCategoryForm(request.POST, request.FILES)
        if category_add_form.is_valid():
            category = category_add_form.save(commit=False)
            category.slug = slugify(category.category_name)
            category.save()

            messages.success(request, 'Category added successfully!')
            return redirect('category_management')  # Redirect to a product listing page or another page
        else:
            messages.error(request, 'Failed to add category. Please correct the errors below.')
    else:
        category_add_form = AddCategoryForm()

    context = {
        'category_add_form': category_add_form
    }
    return render(request, 'myadmin/add_category.html', context)


@admin_required
def delete_category(request,category_id):
    category = get_object_or_404(Category,id=category_id)
    category.delete()
    print('category deleted')
    return redirect('category_management')
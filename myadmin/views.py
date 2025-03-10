from datetime import datetime, time, timedelta
from itertools import product
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from suitup.settings import WKHTMLTOPDF_CMD
from myadmin.reports.sales import daily_sales_report, monthly_sales_report, weekly_sales_report, yearly_sales_report
from myadmin.forms import MyForm
from orders.models import Order, OrderProduct, ReturnProduct
from store.models import Coupon, Product, ProductImage, Stock, Variation
from accounts.models import Account
from category.models import Category
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from store.forms import AddProductForm, AddVariationForm, CouponForm, ProductImageForm
from category.forms import AddCategoryForm
from django.utils.text import slugify
from .utils import admin_required, generate_excel_report, generate_pdf_report, get_filtered_orders
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
# from openpyxl import Workbook
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Exists, OuterRef
from django.utils.timezone import now
from weasyprint import HTML
# import pdfkit
from django.templatetags.static import static
from django.db.models import Count
from functools import reduce
import operator


def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            if user.is_admin:
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

def admin_dashboard(request):
    #Daily sales
    xValues = ["12am-6am", "6am-12pm", "12pm-6pm", "6pm-12am"]
    yValues = []
    for i in range(4):
        start_time = time(6*i, 0)
        end_time = time(6*(i+1)-1, 0)
        order_products = OrderProduct.objects.all()
        order_products_count = order_products.filter(updated_at__time__range=(start_time, end_time)).count()
        yValues.append(order_products_count)
    
    #Weekly Sales
    xValues_week = ["Sun","Mon","Tue","Wed","Thur","Fri","Sat"]
    yValues_week = []
    for i in range(1,8):
        total_sales = OrderProduct.objects.filter(updated_at__week_day=i).count()
        yValues_week.append(total_sales)
        print(yValues_week)

    #Monthly Sales
    xValues_month = ["Jan","Feb","March","April","May","June","Aug","Sept","Oct","Nov","Dec"]
    yValues_month = []
    for i in range(1,13):
        total_sales = OrderProduct.objects.filter(updated_at__month=i).count()
        yValues_month.append(total_sales)
        print(yValues_month)

    #Monthly Sales
    xValues_year = ["2025","2026","2027"]
    yValues_year = []
    for i in range(2025,2028):
        total_sales = OrderProduct.objects.filter(updated_at__year=i).count()
        yValues_year.append(total_sales)
        print(yValues_year)
    
    
    best_selling = Product.objects.annotate(sales_count=Count('product_ordered')).order_by('-sales_count')[:10]
    best_selling_cat = Category.objects.annotate(sales_count=Count('category_product__product_ordered')).order_by('-sales_count')[:10]

    context = {
        'xValues':xValues,
        'yValues':yValues,
        'xValues_week':xValues_week,
        'yValues_week':yValues_week,
        'xValues_month':xValues_month,
        'yValues_month':yValues_month,
        'xValues_year':xValues_year,
        'yValues_year':yValues_year,
        'best_selling':best_selling,
        'best_selling_cat':best_selling_cat,
    }
    return render(request,'myadmin/admin_dashboard.html',context)

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
    categories = Category.objects.all().order_by('id')
    category_add_form = AddCategoryForm()
    context = {
        'categories':categories,
        'category_add_form':category_add_form,
    }
    return render(request,'myadmin/category/category_management.html',context)

@admin_required
def add_category_ajax(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        form = AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            errors = {field: form.errors[field].as_text() for field in form.errors}
            return JsonResponse({"success": False, "errors": errors})
    return JsonResponse({"success": False, "message": "Invalid request"})

@admin_required
def order_management(request):
    
    orders = Order.objects.annotate(has_returns=Exists(OrderProduct.objects.filter(order=OuterRef('pk'), order_return__isnull=False))).order_by('-updated_at')
    context = {
        'orders': orders
    }
    return render(request,'myadmin/order_management.html',context)

@admin_required
def update_order_product_status(request, order_product_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        
        try:
            # Get the OrderProduct object
            order_product = OrderProduct.objects.get(id=order_product_id)
            
            # Update status
            order_product.status = status
            order_product.save()

            # Return a success response with the updated status
            return JsonResponse({
                "success": True,
                "message": "Status updated successfully.",
                "new_status": order_product.status  # Return the updated status
            })
        except OrderProduct.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Order product not found."
            }, status=404)

    return JsonResponse({
        "success": False,
        "message": "Invalid request method."
    }, status=400)

@admin_required
def order_product_return_decision(request, order_product_id):
    print(request.POST)
    if request.method == 'POST':
        decision = request.POST.get('decision')

        if not decision or decision not in ['approved', 'rejected']:
            # Handle invalid or missing decision
            return redirect('order_management')  # or show an error message

        # Fetch the order_product and return_product with error handling
        order_product = get_object_or_404(OrderProduct, id=order_product_id)
        try:
            return_product = ReturnProduct.objects.get(order_product=order_product)
        except ReturnProduct.DoesNotExist:
            # Handle the case where ReturnProduct does not exist
            return redirect('order_management')  # or show an error message

        # Update return product status
        return_product.status = decision
        
        return_product.save()

        # Update order product status based on decision
        if decision == 'rejected':
            order_product.status = 'delivered'
        elif decision == 'approved':
            order_product.status = 'returned'

        order_product.save()

    return redirect('order_management')

@admin_required
def coupon_management(request):
    coupons = Coupon.objects.all()
    coupon_form = CouponForm()
    context = {
        'coupons':coupons,
        'coupon_form':coupon_form,
    }
    return render(request,'myadmin/coupon/coupon_management.html',context)

def add_coupon(request):
    if request.method == 'POST':
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            coupon = coupon_form.save(commit=False)
            coupon.save()
            messages.success(request, 'Coupon added successfully!')
    return redirect('coupon_management')  

@admin_required
def delete_coupon(request,coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    coupon.delete()
    messages.warning(request, 'Coupon deleted')
    return redirect('coupon_management')    


@admin_required
def inventory_management(request):
    products = Product.objects.all()
    variations = Variation.objects.all()
    stocks = Stock.objects.all()
    context = {
        'stocks': stocks,
        'products' : products
    }
    return render(request,'myadmin/inventory/inventory_management.html',context)

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
            messages.error(request, 'Failed to add product. Please correct the errors below.')
    else:
        product_form = AddProductForm()

    context = {
        'product_form': product_form
    }
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
def add_product_variation(request):
    products = Product.objects.all()
    if request.method=='POST':
        variation_form = AddVariationForm(request.POST)
        if variation_form.is_valid():
            variation = variation_form.save(commit=False)
            variation.is_active=True
            variation.save()
            messages.success(request, 'Variation added successfully!')
            return redirect('product_management')
    else:
         variation_form = AddVariationForm()
    context = {
        'variation_form': variation_form,
        'products':products,
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

# @admin_required
# def add_category(request):
#     if request.method == 'POST':
#         category_add_form = AddCategoryForm(request.POST, request.FILES)
#         if category_add_form.is_valid():
#             category = category_add_form.save(commit=False)
#             category.slug = slugify(category.category_name)
#             category.save()

#             messages.success(request, 'Category added successfully!')
#             return redirect('category_management')  # Redirect to a product listing page or another page
#         else:
#             messages.error(request, 'Failed to add category. Please correct the errors below.')
    
#     context = {
#         'category_add_form': category_add_form
#     }
#     return render(request, 'myadmin/category/category_management.html', context)

@admin_required
def delete_category(request,category_id):
    category = get_object_or_404(Category,id=category_id)
    category.delete()
    return redirect('category_management')

#Currently not used, in the update modal itself stock added
@admin_required
def add_product_stock(request,id):
    # Split the string into a list of numbers
    ids = list(map(int,id.split("-")))
    
    # Extract product ID (first element)
    product_id = ids[0]

    # Extract variation IDs (remaining elements)
    Variation_ids = ids[1:]

    #Fetch the product instance
    product_instance  = Product.objects.get(id=product_id)

    #Fetch variation instances
    Variations = Variation.objects.filter(id__in=Variation_ids)

    # create the stock object
    stock_instance = Stock.objects.create(product=product_instance)
    stock_instance.save()  # ✅ Ensure it's saved first
    
    #Assign variations to the ManyToMany field
    stock_instance.variation_combo.set(Variations)

    #save the object
    stock_instance.save()

    messages.success(request,'Stock object created successfully!')
 

    return redirect('inventory_management')

    # if request.method == 'POST':
    #     form = StockForm(request.POST)
    #     if form.is_valid():
    #         stock = form.save(commit=False)
    #         # Generate search key based on product and variations
    #         stock.save()
    #         form.save_m2m()
    #         messages.success(request, 'Stock created successfully.')
    #         return JsonResponse({'success' : True})
    #         # return redirect('inventory_management')
    # else:
    #     form = StockForm()
    #     # Check if the request is AJAX, return only the form content
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     return render(request, 'myadmin/inventory/add_stock_form.html', {'form': form})
    # return render(request, 'myadmin/inventory/add_stock.html', {'form': form, 'title': 'Create Stock'})
    
@admin_required
def update_product_stock(request,variation_id):
    if request.method == "POST":
        new_stock = request.POST.get("new_stock")
        stock_product = get_object_or_404(Stock, id=variation_id)
        stock_product.product_stock = new_stock
        stock_product.save()
        messages.success(request, "Stock updated successfully!")

        # Redirect with query parameter to indicate the modal to open
    return redirect(request.META.get('HTTP_REFERER', '/'))
   
@admin_required  
def update_product_price(request, variation_id):
    if request.method == "POST":
        new_price = request.POST.get("new_price")
        stock_product = get_object_or_404(Stock, id=variation_id)
        stock_product.price = new_price
        stock_product.save()
        messages.success(request, "Price updated successfully!")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@admin_required
def delete_stock(request,stock_id):
    stock = get_object_or_404(Stock,id=stock_id)
    stock.delete()
    messages.warning(request, 'Stock deleted')
    return redirect('inventory_management')

@admin_required
def stock_create_view(request):
    form = StockForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        form.save_m2m()
        # Redirect or show success message
    return render(request, 'stock_create.html', {'form': form})

@admin_required
def load_variations(request):
    product_id = request.GET.get('product_id')
    product_used = Product.objects.get(id=product_id)
    product_name = product_used.product_name
    variations = Variation.objects.filter(product_id=product_id)
  
    variation_dict_ids = {}
    variation_dict_names = {}

    for var in variations:
        category_name = var.variation_category.name  # Get category name (e.g., "Color", "Size")
        if category_name not in variation_dict_ids:
            variation_dict_ids[category_name] = []
            variation_dict_names[category_name] = []
        variation_dict_ids[category_name].append(var.id)  # Store variation IDs under category
        variation_dict_names[category_name].append(f"{var.variation_category.name}-{var.variation_value}")

    
    # Generate all possible combinations
    categories = list(variation_dict_ids.keys())
    category_values_ids = [variation_dict_ids[key] for key in categories]
    category_values_names = [variation_dict_names[key] for key in categories]


    # Create the output list with hyphen-separated format
    combo_list_ids = [f"{product_id}-{'-'.join(map(str, combo))}" for combo in product(*category_values_ids)]
    combo_list_names = [f"{product_name}-{'-'.join(map(str, combo))}" for combo in product(*category_values_names)]
    print(f"Combo_list_ids : {combo_list_ids}")
    print(f"Combo_list_names : {combo_list_names}")

    stock_combo=[]
    stocks = Stock.objects.filter(product_id=product_id)
    for stock in stocks:
        stock_combo.append(stock.search_key)

    print(f"Stock_combo : {stock_combo}")
    for i in stock_combo:
        if i in combo_list_ids:
            combo_list_ids.remove(i)
    print(f"updated Combo_list : {combo_list_ids}")

    # variations_json = variations.values('id','variation_category__name','variation_value')
    # print(variations_json)
    # return JsonResponse(list(variations_json), safe=False)
    return JsonResponse({
        "combo_list_ids": combo_list_ids,
        "combo_list_names": combo_list_names,
    })

@admin_required
def sales_report_filter(request):
    return render(request,'myadmin/sales_report/sales_report.html')

@admin_required
def sales_report(request):
    sale_report = None
    if request.method == 'GET':
        report_type = request.GET.get('report-type')
        if report_type == 'daily':
            sale_date = request.GET.get('daily-date')
            print(f"sale date : {sale_date}")
            sale_report = daily_sales_report(request,sale_date)
        elif report_type == 'weekly':
            sale_date = request.GET.get('weekly-date')
            print(f"sale date : {sale_date}")
            sale_report = weekly_sales_report(request,sale_date)
        elif report_type == 'monthly':
            sale_month = request.GET.get('monthly-month')
            print(f"sale month : {sale_month}")
            sale_report = monthly_sales_report(request,sale_month)
        elif report_type == "yearly":
            sale_year = request.GET.get('yearly-year')
            print(f"sale year : {sale_year}")
            sale_report = yearly_sales_report(request,sale_year)
           
    return render(request, 'myadmin/sales_report/sales_report.html', sale_report)

@admin_required
def export_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Age"])
    ws.append(["John", 25])
    ws.append(["Jane", 30])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="output.xlsx"'
    wb.save(response)
    return response

@admin_required
def generate_pdf_from_template(request,sale_date):
    # Render the HTML template
    sale_report = dict(request.GET)
    sale_report = daily_sales_report(request,sale_date)
    # sale_report['logo_url']=request.build_absolute_uri(static('images/suitup_logo.png'))
    
    html_content = render_to_string('myadmin/sales_report/sales_report_export.html',sale_report)

    # Generate the PDF
    pdf = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    # Return the response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="output.pdf"'  # Change to 'inline' for in-browser view
    return response


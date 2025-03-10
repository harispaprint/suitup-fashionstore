import calendar
from django.db.models import Sum, Count, F,Avg
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from datetime import date, datetime, time, timedelta
from django.http import HttpResponse
from store.models import Product
from orders.models import Order,OrderProduct
# import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
# from weasyprint import HTML
from django.conf import settings
import os

def daily_sales_report(request,sale_date):
    best_selling_product = None
    # sale_date = date(2025, 1, 19)
    print(f"from daily_sales_report {sale_date}")
    order_products = OrderProduct.objects.filter(updated_at__date=sale_date).order_by('updated_at')
    # print(f"order products :{order_products.created_at}")
    daily_total = order_products.aggregate(daily_total_amount = Sum('product_price'))['daily_total_amount'] or 0
    best_selling = order_products.values('product').annotate(sales_count=Count('product')).order_by('-sales_count').first()
    if best_selling is not None:
        best_selling_product_id = best_selling['product']
        best_selling_product = Product.objects.get(id=best_selling_product_id)
    orders = Order.objects.filter(created_at__date=sale_date)
    total_discount = orders.aggregate(discount = Sum(F('sub_order_total') - F('net_order_total')))['discount']
    average_sale_per_transaction = round(orders.aggregate(avg_sale = Avg('grand_order_total'))['avg_sale'] or 0,1)

    result = {'order_prodcuts':order_products,
              'daily_total': daily_total,
              'best_selling_product':best_selling_product,
              'average_sale_per_transaction':average_sale_per_transaction,
              'report_type':'daily',
              'sale_date':sale_date,
              'total_discount':total_discount
              }
    print(result)
    return result

def weekly_sales_report(request,sale_date):
    
    # sale_date = "2025-01-22"
    weekly_total=0
    end_date = datetime.strptime(sale_date, "%Y-%m-%d").date()
    start_date = end_date - timedelta(days=6)

    print(f"from weekly_sales_report start_date{start_date} and end_date{end_date} ")  
    order_products = OrderProduct.objects.filter(updated_at__date__range=[start_date, end_date])
    print(f"ordered products {order_products}")
    daily = {}
    
    current_date = start_date

    while current_date <= end_date:

        current_date+=timedelta(days=1)
        daily_order_products = order_products.filter(updated_at__date=current_date)
        daily_total = daily_order_products.aggregate(weekly_total=Sum('product_price'))['weekly_total'] or 0
        weekly_total+=daily_total
        daily[current_date] = {'daily_total' : daily_total,
                            'daily_order_products': daily_order_products,
                            }
        print(daily[current_date])
    

    best_selling = order_products.values('product').annotate(sales_count=Count('product')).order_by('-sales_count').first()
    best_selling_product_id = best_selling['product']
    best_selling_product = Product.objects.get(id=best_selling_product_id)
    orders = Order.objects.filter(updated_at__date__range=[start_date, end_date])
    average_sale_per_transaction = round(orders.aggregate(avg_sale = Avg('grand_order_total'))['avg_sale'] or 0,1)
    result = {'weekly_total':weekly_total,
              'best_selling_product':best_selling_product,
              'average_sale_per_transaction':average_sale_per_transaction,
              'daily':daily,
              'report_type':'weekly',
              'start_date':start_date,
              'end_date':end_date,
              }
    print(result)
    return result

def monthly_sales_report(request,sale_month):
    monthly_total=0
    year, month = map(int, sale_month.split('-'))
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)

    print(f"from weekly_sales_report start_date{start_date} and end_date{end_date} ")  
    order_products = OrderProduct.objects.filter(updated_at__date__range=[start_date, end_date])
    print(f"ordered products {order_products}")
    week = {}

    week_start_date = start_date
    count = 0
    while week_start_date <= end_date:
        count+=1
        print(f"count{count}")
        week_end_date = week_start_date+timedelta(days=6)
        if week_end_date > end_date:
            week_end_date = end_date
        week_order_products = order_products.filter(updated_at__date__range=[week_start_date,week_end_date])
        weekly_total = week_order_products.aggregate(weekly_total=Sum('product_price'))['weekly_total'] or 0
        monthly_total+=weekly_total
        week_start_date = week_end_date + timedelta(days=1)
        week[count] = {'weekly_total' : weekly_total,
                       'week_order_products': week_order_products,
                       }
        print(week[count])
  
    best_selling = order_products.values('product').annotate(sales_count=Count('product')).order_by('-sales_count').first()
    best_selling_product_id = best_selling['product']
    best_selling_product = Product.objects.get(id=best_selling_product_id)
    orders = Order.objects.filter(updated_at__date__range=[start_date, end_date])
    average_sale_per_transaction = round(orders.aggregate(avg_sale = Avg('grand_order_total'))['avg_sale'] or 0,1)
    result = {'monthly_total':monthly_total,
              'best_selling_product':best_selling_product,
              'average_sale_per_transaction':average_sale_per_transaction,
              'week':week,
              'report_type':'monthly',
              'start_date':start_date,
              'end_date':end_date,
              }
    print(result)
    return result

def yearly_sales_report(request,sale_year):
    yearly_total=0
    sale_year = int(sale_year)

    start_date = datetime(sale_year, 1, 1)
    last_day = calendar.monthrange(sale_year, 12)[1]
    end_date = datetime(sale_year, 12, last_day)

 
    order_products = OrderProduct.objects.filter(updated_at__date__range=[start_date, end_date])
   
    month = {}
    month_no = 0
    print(type(month))
    current_date = datetime.now()
    current_month = current_date.month
    print(current_month,type(current_month))
    current_day = current_date.day
    while month_no < current_month:
        month_no+=1
        month_start_date = datetime(sale_year, month_no, 1)
        if month_no < current_month:
            last_day = calendar.monthrange(sale_year, month_no)[1]
        else:
            last_day = current_day
       
        month_end_date = datetime(sale_year, month_no, last_day)
        month_order_products = order_products.filter(updated_at__date__range=[month_start_date,month_end_date])
        monthly_total = month_order_products.aggregate(monthly_total=Sum('product_price'))['monthly_total'] or 0
        yearly_total+=monthly_total
        month_name = calendar.month_name[month_no]
        month[month_name] = {'monthly_total' : monthly_total,
                            'month_order_products': month_order_products,}
   
    best_selling = order_products.values('product').annotate(sales_count=Count('product')).order_by('-sales_count').first()
    best_selling_product_id = best_selling['product']
    best_selling_product = Product.objects.get(id=best_selling_product_id)
    orders = Order.objects.filter(updated_at__date__range=[start_date, end_date])
    average_sale_per_transaction = round(orders.aggregate(avg_sale = Avg('grand_order_total'))['avg_sale'] or 0,1)
    result = {
              'yearly_total':yearly_total,
              'best_selling_product':best_selling_product,
              'average_sale_per_transaction':average_sale_per_transaction,
              'month':month,
              'report_type':'yearly',
              'start_date':start_date,
              'end_date':end_date,
              }
    print(result)
    return result




def generate_chart():
    # Data for the chart
    x_values = ['Jan', 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    y_values = [7, 8, 8, 9, 9, 9, 10, 11, 14, 14, 1]

    # Create the chart using Matplotlib
    plt.figure(figsize=(6, 4))
    plt.plot(x_values, y_values, color='blue', marker='o')
    plt.title("Sales over Time")
    plt.xlabel("Months")
    plt.ylabel("Sales")
    
    # Save the chart to a BytesIO object (in memory)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)  # Go to the start of the BytesIO object
    
    # Save the chart image to a file if needed (optional)
    # with open(os.path.join(settings.BASE_DIR, 'chart.png'), 'wb') as f:
    #     f.write(image_stream.read())

    # Convert image to a base64 string if you need to send it to the frontend (optional)
    # chart_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    # Create a context with the image
    
    app_static_dir = os.path.join(settings.BASE_DIR, 'suitup', 'static', 'images')
    
    os.makedirs(app_static_dir, exist_ok=True)
    chart_image_path = os.path.join(app_static_dir, 'chart.png')

    # Save the chart to the static directory
    plt.savefig(chart_image_path, format='png')

    return chart_image_path

    



        
    


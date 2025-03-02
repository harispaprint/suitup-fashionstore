from django.http import HttpResponse, HttpResponseForbidden
from functools import wraps

from orders.models import Order

from datetime import timedelta
from django.db.models import Sum, F, Q
from django.utils.timezone import now
import pandas as pd
from reportlab.pdfgen import canvas


def admin_required(view_func):
    """
    Custom decorator to restrict access to admin users.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        if not request.user.is_staff:  # Check if the user is an admin
            return HttpResponseForbidden("Access restricted to admin users only.")
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def get_filtered_orders(filter_type=None, start_date=None, end_date=None):
    today = now().date()
    if filter_type == 'daily':
        start_date = today
        end_date = today + timedelta(days=1)
    elif filter_type == 'weekly':
        start_date = today - timedelta(days=7)
        end_date = today
    elif filter_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif filter_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif start_date and end_date:
        start_date = start_date
        end_date = end_date + timedelta(days=1)

    return Order.objects.filter(created_at__gte=start_date,created_at__lt=end_date,is_ordered=True)

def generate_pdf_report(context):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="sales_report.pdf"'
    p = canvas.Canvas(response)

    # Add report title
    p.drawString(100, 800, "Sales Report")
    
    # Example of adding text
    p.drawString(100, 780, f"Overall Sales Count: {context['overall_sales_count']}")
    p.drawString(100, 760, f"Overall Order Amount: {context['overall_order_amount']}")
    p.drawString(100, 740, f"Overall Discount: {context['overall_discount']}")

    p.showPage()
    p.save()
    return response

def generate_excel_report(context):
    orders = context['orders']
    data = [{
        'Order Number': order.order_number,
        'Order Amount': order.grand_order_total,
        'Discount': order.sub_order_total - order.net_order_total,
        'Created At': order.created_at,
    } for order in orders]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    df.to_excel(response, index=False)
    return response

from store.models import Product, Stock

# def get_search_key(product,request):
#     search_key = None
#     if request.method == "GET":
#         variations = ", ".join([f"{key}{str(request.GET.get(key))}" for key in request.GET])
#         search_key = f"{product.product_name}{variations}"
#     elif request.method == "POST":
#         variations = ", ".join([f"{key}{value}" for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'])
#         search_key = f"{product.product_name}{variations}"
#         print(search_key)
#     return search_key

def get_search_key(product, request):
    search_key = None
    if request.method == "GET":
        variation_ids = "-".join([str(request.GET.get(key)) for key in request.GET if request.GET.get(key)])
        search_key = f"{product.id}-{variation_ids}" if variation_ids else str(product.id)
    elif request.method == "POST":
        variation_ids = "-".join([str(value) for key, value in request.POST.items() if key != 'csrfmiddlewaretoken' and value.isdigit()])
        search_key = f"{product.id}-{variation_ids}" if variation_ids else str(product.id)
    return search_key

def get_product_stock(search_key):
    try:
        specific_stock = Stock.objects.get(search_key__iexact=search_key)
        return specific_stock
        # return [specific_stock.product_stock,specific_stock.price]
    except Stock.DoesNotExist:
        return 0
    except Stock.MultipleObjectsReturned:
        return 0
    
def update_stock(request,product,variation_combo_value,new_stock):
    specific_stock = Stock.objects.filter(product=product,variation_combo__variation_value__in=variation_combo_value).distinct().first()
    specific_stock.stock=new_stock
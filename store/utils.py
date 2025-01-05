from store.models import Product, Stock

def get_search_key(product,request):
    search_key = None
    if request.method == "GET":
        print(f" this is request.get {request.GET}")
        variations = ", ".join([f"{key}{str(request.GET.get(key))}" for key in request.GET])
        search_key = f"{product.product_name}{variations}"
        print(f"Search - {search_key}")
    elif request.method == "POST":
        print(f" this is request.post {request.POST}")
        variations = ", ".join([f"{key}{value}" for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'])
        search_key = f"{product.product_name}{variations}"
        print(f"Search - {search_key}")
    return search_key

def get_product_stock(search_key):
    print('get_product_stock')
    try:
        specific_stock = Stock.objects.get(search_key__iexact=search_key)
        return specific_stock
        # return [specific_stock.product_stock,specific_stock.price]
    except Stock.DoesNotExist:
        print("No stock found.")
        return 0
    except Stock.MultipleObjectsReturned:
        print("Multiple stock records found for the given key.")
        return 0
    
def update_stock(request,product,variation_combo_value,new_stock):
    specific_stock = Stock.objects.filter(product=product,variation_combo__variation_value__in=variation_combo_value).distinct().first()
    specific_stock.stock=new_stock
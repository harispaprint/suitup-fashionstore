from store.models import Stock

def get_product_stock(search_key):
    print('get_product_stock')
    try:
        specific_stock = Stock.objects.get(search_key=search_key)
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
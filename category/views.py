
from django.shortcuts import render
from category.models import Category
from django.db.models import Q

def category(request):
    sort = request.GET.get('sort', 'category_name')
    categories = Category.objects.all().order_by(sort)
    
    categories_count = categories.count()
    #Pagination logic
    # paginator = Paginator(products, 3)  # Show 6 products per page.
    # page_number = request.GET.get("page")
    # paged_products = paginator.get_page(page_number)
    
    context = {
       'categories':categories,
       'categories_count':categories_count,
       'is_product_page': False,

      }
    return render(request,'store/category.html',context)

def search_category(request):
    categories = []
    categories_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword.strip():  # Ensure the keyword is not empty or only whitespace
            # Apply filtering logic using Q object
            categories = Category.objects.filter(
                Q(category_name__icontains=keyword) | Q(description__icontains=keyword)
            )
            categories_count = categories.count()
    
    context = {
        
        'categories': categories,
        'categories_count': categories_count,  # Corrected the variable name
        'is_product_page': False,

    }
    return render(request, 'store/category.html', context)
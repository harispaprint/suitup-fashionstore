from store.models import Wishlist
from store.views import wishlist

def wishlist_counter(request):
    wishlist_count = 0
    if 'admin' in request.path:
        return {}
    else:
        if request.user.is_authenticated:
            try:
                wishlist = Wishlist.objects.filter(user=request.user)
                for list in wishlist:
                    wishlist_count += 1
            except Wishlist.DoesNotExist:
                wishlist_count = 0
    return dict(wishlist_count=wishlist_count)

def breadcrumbs_processor(request):
    path = request.path.strip('/').split('/')
    breadcrumbs = [{'url': '/', 'label': 'Home'}]
    for i in range(len(path)):
        url = '/' + '/'.join(path[:i + 1]) + '/'
        label = path[i].replace('-', ' ').capitalize()
        breadcrumbs.append({'url': url, 'label': label})
    return {'breadcrumbs': breadcrumbs}


from carts.models import CartItem
from carts.views import _cart_id,Cart

# def menu_links(request):
#     links = Category.objects.all()

#     return dict(links=links)

#To calcualte total items in cart
def cart_quantity(request):
    cart_quantity=0
    cart_items = CartItem.objects.filter(cart__cart_id = _cart_id(request))
    print('position 3')
    for cart_item in cart_items:
        cart_quantity+=cart_item.quantity
    return dict(cart_quantity=cart_quantity)

#Alternative method
def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            print('position 4')
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_instance = cart.first()
                cart_items = CartItem.objects.filter(cart=cart_instance)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
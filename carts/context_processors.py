from carts.models import CartItem
from carts.views import _cart_id

# def menu_links(request):
#     links = Category.objects.all()

#     return dict(links=links)

def cart_quantity(request):
    cart_quantity=0
    cart_items = CartItem.objects.filter(cart__cart_id = _cart_id(request))
    for cart_item in cart_items:
        cart_quantity+=cart_item.quantity
    return dict(cart_quantity=cart_quantity)
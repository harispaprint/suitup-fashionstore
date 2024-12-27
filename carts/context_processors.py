from carts.models import CartItem
from carts.views import _cart_id,Cart


def counter(request):
    cart_count = 0
    cart_items=[]
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            print(cart)
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            elif cart.exists():
                cart_instance = cart.first()
                print(cart_instance)
                cart_items = CartItem.objects.filter(cart=cart_instance)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
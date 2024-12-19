from carts.models import Cart

def _cart_id(request):
    try:
         cart_id = request.session.session_key
         print(f"cart_id from session key : {cart_id}")
    except:
        cart = Cart.objects.latest('date_added').cart_id
        cart_id = cart.cart_id
        print(f"cart_id from date added : {cart_id}")

   
    if not cart_id:
        cart_id = request.session.create()
    return cart_id
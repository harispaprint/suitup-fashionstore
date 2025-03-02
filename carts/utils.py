from carts.models import Cart, CartItem

def _cart_id(request):
    try:
         cart_id = request.session.session_key
    except:
        cart = Cart.objects.latest('date_added').cart_id
        cart_id = cart.cart_id

   
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

def _coupon_user_id(request):
    try:
         coupon_user_id = request.session.session_key
    except:
        pass
   
    if not coupon_user_id:
        coupon_user_id = request.session.create()
    return coupon_user_id

def cart_check(request):
    current_user = request.user
    cart_gen=None
    cart_user=None
    try:
        cart_gen = Cart.objects.latest('date_added')
        print(f"in cart check {cart_gen}")
        is_cart_item_gen_exists = CartItem.objects.filter(cart=cart_gen,user=None).exists()
        if is_cart_item_gen_exists:
            cart_item_gen = CartItem.objects.filter(cart=cart_gen,user=None)

            cart_items_user = CartItem.objects.filter(user=current_user)
            if cart_items_user.first() is not None:    
                cart_user = cart_items_user.first().cart
            
                for item in cart_item_gen:
                    try:
                        cart_item_swap = cart_items_user.get(user=current_user,stock=item.stock)
                        cart_item_swap.quantity= cart_item_swap.quantity+item.quantity
                        cart_item_swap.save()
                        item.delete()
                    except CartItem.DoesNotExist:
                        item.user = current_user
                        item.cart = cart_user
                        item.save()
            else:
                for item in cart_item_gen:
                    item.user = current_user
                    item.save()

        if cart_user is not None:
            cart_gen.delete()
        
    except:
        pass

def get_user_cart_id(request):
    cart_user_id = None
    current_user = request.user
    cart_items_user = CartItem.objects.filter(user=current_user)
    if cart_items_user.first() is not None:    
        cart_user_id = cart_items_user.first().cart.id
    return cart_user_id
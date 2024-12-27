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

def cart_check(request):
    user = request.user
    try:
        cart = Cart.objects.latest('date_added')
        is_cart_item_exists = CartItem.objects.filter(cart=cart,user=None).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(cart=cart,user=None)

            # Getting the product variations by cart id
            product_variation = []
            for item in cart_item:
                variation = item.variations.all()
                product_variation.append(list(variation))

            # Get the cart items from the user to access his product variations
            cart_item = CartItem.objects.filter(user=user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            for pr in product_variation:
                if pr in ex_var_list:
                    index = ex_var_list.index(pr)
                    item_id = id[index]
                    item = CartItem.objects.get(id=item_id)
                    item.quantity += 1
                    item.user = user
                    item.save()
                else:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = user
                        item.save()
        cart.delete()
    except:
        pass
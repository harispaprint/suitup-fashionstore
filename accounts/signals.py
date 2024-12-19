from accounts.models import UserProfile
from carts.models import Cart, CartItem
from carts.utils import _cart_id

from allauth.account.signals import user_signed_up,user_logged_in # type: ignore
from django.dispatch import receiver

@receiver(user_signed_up)
def activate_social_user(sender, request, user, **kwargs):
    user.is_active = True  # Activate the user account
    user.save()
    userprofile = UserProfile.objects.create(user=user)


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    try:
        # Get the session cart
        session_cart = Cart.objects.get(cart_id=_cart_id(request))
        print('Postion 5 signal')
        session_cart_items = CartItem.objects.filter(cart=session_cart)

        if session_cart_items.exists():
            # Get the user's existing cart items
            user_cart_items = CartItem.objects.filter(user=user)

            # Prepare data for matching variations
            session_variations = [
                list(item.variations.all()) for item in session_cart_items
            ]
            user_variations = [
                list(item.variations.all()) for item in user_cart_items
            ]

            for session_item in session_cart_items:
                session_item_variations = list(session_item.variations.all())
                
                if session_item_variations in user_variations:
                    # If variation exists in user's cart, update quantity
                    index = user_variations.index(session_item_variations)
                    user_item = user_cart_items[index]
                    user_item.quantity += session_item.quantity
                    user_item.save()
                else:
                    # Otherwise, reassign the session cart item to the user
                    session_item.user = user
                    session_item.cart = None  # Detach from the session cart
                    session_item.save()

        # Clean up the session cart after merging
        session_cart.delete()
    except Cart.DoesNotExist:
        pass
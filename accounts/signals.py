from accounts.models import UserProfile
from carts.models import Cart, CartItem
from carts.utils import _cart_id,cart_check

from allauth.account.signals import user_signed_up,user_logged_in # type: ignore
from django.dispatch import receiver

@receiver(user_signed_up)
def activate_social_user(sender, request, user, **kwargs):
    user.is_active = True  # Activate the user account
    user.save()
    userprofile = UserProfile.objects.create(user=user)


# social_account_added

@receiver(user_logged_in)
def cartitem_to_user(sender, request, user, **kwargs):
    print(f"17 {user}")
    cart_check(request)
    # try:
    #     cart = Cart.objects.order_by('-date_added').first()
    #     cartitems = CartItem.objects.filter(cart=cart)
    #     for cartitem in cartitems:
    #         print(cartitem)
    #         cartitem.user=user
    #         # cartitem.cart=None
    #         cartitem.save()
    # except:
    #     pass

from allauth.account.signals import user_signed_up # type: ignore
from django.dispatch import receiver

@receiver(user_signed_up)
def activate_social_user(sender, request, user, **kwargs):
    user.is_active = True  # Activate the user account
    user.save()
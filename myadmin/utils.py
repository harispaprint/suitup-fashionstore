from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    """
    Custom decorator to restrict access to admin users.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        if not request.user.is_staff:  # Check if the user is an admin
            return HttpResponseForbidden("Access restricted to admin users only.")
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

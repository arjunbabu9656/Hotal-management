from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.is_superuser or request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Redirect to a custom 403 page or raise PermissionDenied
                # For this project, we'll try to redirect to a specific 403 URL if it exists
                # or just raise the exception which we will handle later.
                raise PermissionDenied
        return _wrapped_view
    return decorator

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
            
            # Superusers (Owners) have access to everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # Role check
            if hasattr(request.user, 'profile') and request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied
        return _wrapped_view
    return decorator

def owner_required(view_func):
    """Decorator for views that strictly require the Owner role."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Check if superuser or role is owner
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'owner'):
            return view_func(request, *args, **kwargs)
        
        raise PermissionDenied
    return _wrapped_view

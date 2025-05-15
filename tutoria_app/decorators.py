from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def admin_required(view_func):
    """Custom decorator to ensure only admins can access a view."""
    @wraps(view_func)
    @login_required(login_url='adminlogin')  # Redirects unauthorized users to admin login
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
            return redirect('adminlogin')  # Redirects non-admin users to admin login
        return view_func(request, *args, **kwargs)
    
    return wrapper




def user_login_required(view_func):
    """Custom decorator to redirect non-logged-in users to login page."""
    @wraps(view_func)
    @login_required(login_url='signin')  
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper

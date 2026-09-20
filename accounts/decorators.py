from functools import wraps
from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def login_required_mongo(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'mongo_user', None):
            messages.warning(request, 'Please log in to continue.')
            login_url = reverse('accounts:login')
            query = urlencode({'next': request.get_full_path()})
            return redirect(f'{login_url}?{query}')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, 'mongo_user', None)
        if not user:
            messages.warning(request, 'Please log in to continue.')
            return redirect('accounts:login')
        if not user.is_admin:
            messages.error(request, 'You do not have permission to access the admin area.')
            return redirect('cars:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def current_user(request):
    """Makes the logged-in user available in every template as `current_user`."""
    user = getattr(request, 'mongo_user', None)
    return {
        'current_user': user,
        'is_authenticated_user': user is not None,
        'is_admin_user': bool(user and user.is_admin),
    }

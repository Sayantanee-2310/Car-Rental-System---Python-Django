from accounts.models import User


class MongoUserMiddleware:
    """Attaches the logged-in MongoDB user (if any) to request.mongo_user."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.mongo_user = None
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = User.objects(user_id=user_id, is_active=True).first()
                request.mongo_user = user
            except Exception:
                request.mongo_user = None
        response = self.get_response(request)
        return response

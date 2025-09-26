from django.conf import settings

class AdminSeparateSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If user is visiting the admin site, use a different cookie
        if request.path.startswith("/admin/"):
            settings.SESSION_COOKIE_NAME = "admin_sessionid"
        else:
            settings.SESSION_COOKIE_NAME = "frontend_sessionid"

        response = self.get_response(request)
        return response
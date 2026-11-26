import re
from django.utils.html import strip_tags

class SanitizePostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and not request.path.startswith('/admin/'):
            mutable_post = request.POST.copy()
            for key, values in mutable_post.lists():
                if 'password' in key or key == 'csrfmiddlewaretoken':
                    continue
                cleaned = []
                for val in values:
                    val = strip_tags(val)
                    val = re.sub(r'(?i)(javascript|vbscript|data):', '', val)
                    cleaned.append(val)
                mutable_post.setlist(key, cleaned)
            request.POST = mutable_post
        return self.get_response(request)

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith('/admin/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://googleapis.com; "
                "font-src 'self' https://gstatic.com data:; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none';"
            )
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

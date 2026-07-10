from .models import AccessLog


class AccessLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if request.user.is_authenticated:

            path = request.path

            ignore_urls = [
                "/admin/",
                "/static/",
                "/favicon.ico",
            ]

            if not any(path.startswith(x) for x in ignore_urls):

                AccessLog.objects.create(
                    user=request.user,
                    username=request.user.username,
                    menu=path,
                    url=path,
                    ip=get_client_ip(request)
                )

        return response

def get_client_ip(request):

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")
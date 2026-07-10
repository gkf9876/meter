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
                    ip=request.META.get("REMOTE_ADDR")
                )

        return response
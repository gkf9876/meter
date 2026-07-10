from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import LoginLog


@receiver(user_logged_in)
def save_login_log(sender, request, user, **kwargs):

    ip = request.META.get("REMOTE_ADDR")

    user_agent = request.META.get("HTTP_USER_AGENT", "")

    LoginLog.objects.create(
        user=user,
        username=user.username,
        ip=get_client_ip(request),
        user_agent=user_agent,
        success=True
    )

def get_client_ip(request):

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")
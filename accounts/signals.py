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
        ip=ip,
        user_agent=user_agent,
        success=True
    )
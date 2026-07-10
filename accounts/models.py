from django.db import models
from django.contrib.auth.models import User


class LoginLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    username = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["-login_time"]

    def __str__(self):
        return f"{self.username} ({self.login_time})"

class AccessLog(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )

    username = models.CharField(max_length=100)
    menu = models.CharField(max_length=200)
    url = models.CharField(max_length=300)
    ip = models.GenericIPAddressField()
    access_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-access_time"]
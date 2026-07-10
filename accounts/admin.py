from django.contrib import admin

from .models import LoginLog, AccessLog


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "ip",
        "login_time",
        "success",
    )

    search_fields = (
        "username",
        "ip",
    )

    list_filter = (
        "success",
        "login_time",
    )


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "menu",
        "ip",
        "access_time",
    )

    search_fields = (
        "username",
        "menu",
    )

    list_filter = (
        "access_time",
    )
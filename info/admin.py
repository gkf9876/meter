from django.contrib import admin

from .models import Info


class InfoAdmin(admin.ModelAdmin):
    search_fields = ['content']

admin.site.register(Info, InfoAdmin)
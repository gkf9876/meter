from django.contrib import admin

from .models import File


class FileAdmin(admin.ModelAdmin):
    search_fields = ['file']

admin.site.register(File, FileAdmin)
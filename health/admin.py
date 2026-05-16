from django.contrib import admin
from .models import Health, HealthDetail

class HealthAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Health, HealthAdmin)
admin.site.register(HealthDetail)
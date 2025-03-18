from django.contrib import admin
from .models import Mission, MissionDetail

class MissionAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Mission, MissionAdmin)
admin.site.register(MissionDetail)
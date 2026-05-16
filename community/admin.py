from django.contrib import admin
from .models import Community, CommunityDetail

class CommunityAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityDetail)
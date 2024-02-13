from django.contrib import admin
from memorization.models import Memorization

class MemorizationAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Memorization, MemorizationAdmin)
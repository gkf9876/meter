from django.contrib import admin
from .models import Doit, DoitDetail

class DoitAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Doit, DoitAdmin)
admin.site.register(DoitDetail)
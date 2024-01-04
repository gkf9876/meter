from django.contrib import admin
from .models import Study, Meter

class StudyAdmin(admin.ModelAdmin):
    search_fields = ['name']

class MeterAdmin(admin.ModelAdmin):
    search_fields = ['study__name']

# Register your models here.
admin.site.register(Study, StudyAdmin)
admin.site.register(Meter, MeterAdmin)
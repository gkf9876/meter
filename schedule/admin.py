from django.contrib import admin
from .models import Schedule, ScheduleDetail, ScheduleItem


class ScheduleAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(ScheduleDetail)
admin.site.register(ScheduleItem)
from django.contrib import admin
from .models import ThirdHabit, ThirdHabitItem, ThirdHabitDetail, ThirdHabitItemDetail, ThirdHabitItemDetailTime


class ThirdHabitAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(ThirdHabit, ThirdHabitAdmin)
admin.site.register(ThirdHabitItem)
admin.site.register(ThirdHabitItemDetail)
admin.site.register(ThirdHabitItemDetailTime)
admin.site.register(ThirdHabitDetail)
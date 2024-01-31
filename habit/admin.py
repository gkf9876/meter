from django.contrib import admin
from .models import Habit, HabitDetail

class HabitAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Habit, HabitAdmin)
admin.site.register(HabitDetail)
from django.contrib import admin
from .models import ThirdHabit, ThirdHabitItem

class ThirdHabitAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(ThirdHabit, ThirdHabitAdmin)
admin.site.register(ThirdHabitItem)
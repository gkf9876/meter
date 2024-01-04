from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Todo, TodoDetail


class TodoAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'indented_title',
        'subject',
    )

class TodoDetailAdmin(admin.ModelAdmin):
    search_fields = ['todo__subject']

admin.site.register(Todo, TodoAdmin)
admin.site.register(TodoDetail, TodoDetailAdmin)
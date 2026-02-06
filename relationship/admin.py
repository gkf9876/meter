from django.contrib import admin
from .models import Relationship, RelationshipDetail

class RelationshipAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(RelationshipDetail)
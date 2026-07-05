from django.contrib import admin
from .models import Tag,TaggedItem
# Register your models here.

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('label',)
    search_fields = ('label',)
    ordering = ('label',)

@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ('tag', 'content_object')
    list_filter = ('tag',)
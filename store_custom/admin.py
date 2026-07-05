from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from catalog.models import Product
from catalog.admin import ProductAdmin
from tags.models import Tag, TaggedItem
# Register your models here.


class TagInline(GenericTabularInline):
    model = TaggedItem
    extra = 1
    
class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]

admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
from django.contrib import admin
from .models import Reference

# Register your models here.
#admin.site.register(Reference)

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display=('title','slug', 'description', 'link', 'author', 'created', 'updated')
    list_filter=('created','updated', 'author')
    search_fields=('title', 'description')
    prepopulated_fields={'slug':('title',)}
    raw_id_fields = ('author',)
    date_hierarchy='created'
    ordering = ('created','updated')

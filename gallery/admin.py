#!/usr/bin/env python

from django.contrib import admin
from .models import Album, AlbumPage, PageLayout, Photo

class AlbumAdmin(admin.ModelAdmin):
    readonly_fields = ("share_id", "created_at")

admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumPage)
admin.site.register(PageLayout)
admin.site.register(Photo)
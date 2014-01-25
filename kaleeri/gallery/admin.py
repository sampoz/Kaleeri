#!/usr/bin/env python

from django.contrib import admin
from .models import Album, AlbumPage, PageLayout, Photo

admin.site.register(Album)
admin.site.register(AlbumPage)
admin.site.register(PageLayout)
admin.site.register(Photo)
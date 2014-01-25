#!/usr/bin/env python

from django.contrib import admin
from .models import Gallery, GalleryPage, PageLayout, Photo

admin.site.register(Gallery)
admin.site.register(GalleryPage)
admin.site.register(PageLayout)
admin.site.register(Photo)
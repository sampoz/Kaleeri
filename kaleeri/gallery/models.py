#!/usr/bin/env python

import django.contrib.auth.models
from django.db import models


class Gallery(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    owner = models.ForeignKey(django.contrib.auth.models.User)
    name = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    share_id = models.CharField(max_length=40, blank=True, null=True)


class PageLayout(models.Model):
    name = models.CharField(max_length=32)
    css_class = models.CharField(max_length=32)
    num_photos = models.IntegerField()


class GalleryPage(models.Model):
    gallery = models.ForeignKey(Gallery)
    layout = models.ForeignKey(PageLayout)
    num = models.IntegerField()
    text = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('num',)


class Photo(models.Model):
    page = models.ForeignKey(GalleryPage)
    url = models.URLField()
    num = models.IntegerField()
    crop_x = models.IntegerField()
    crop_y = models.IntegerField()
    crop_w = models.IntegerField()
    crop_h = models.IntegerField()

    class Meta:
        ordering = ('num',)
#!/usr/bin/env python

import django.contrib.auth.models
from django.db import models
from django.db.models import Sum


class Album(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    owner = models.ForeignKey(django.contrib.auth.models.User)
    name = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    share_id = models.CharField(max_length=40, blank=True, null=True)

    def get_num_photos(self):
        return self.albumpage_set.aggregate(Sum('photoset__count'))

    def get_max_photos(self):
        return self.albumpage_set.aggregate(Sum('layout__num_photos'))

    def has_user_access(self, user):
        return user is self.owner


class PageLayout(models.Model):
    name = models.CharField(max_length=32)
    css_class = models.CharField(max_length=32)
    num_photos = models.IntegerField()


class AlbumPage(models.Model):
    album = models.ForeignKey(Album)
    layout = models.ForeignKey(PageLayout)
    num = models.IntegerField()

    class Meta:
        ordering = ('num',)


class Photo(models.Model):
    page = models.ForeignKey(AlbumPage)
    url = models.URLField()
    num = models.IntegerField()
    caption = models.TextField(blank=True)
    crop_x = models.IntegerField()
    crop_y = models.IntegerField()
    crop_w = models.IntegerField()
    crop_h = models.IntegerField()

    class Meta:
        ordering = ('num',)
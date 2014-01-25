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
        return self.albumpage_set.aggregate(Sum('photo'))["photo__sum"] or 0

    def get_max_photos(self):
        return self.albumpage_set.aggregate(Sum('layout__num_photos'))["layout__num_photos__sum"] or 0

    def has_user_access(self, user):
        return user == self.owner

    def __unicode__(self):
        return self.name


class PageLayout(models.Model):
    name = models.CharField(max_length=32)
    css_class = models.CharField(max_length=32)
    num_photos = models.IntegerField()

    def __unicode__(self):
        return self.name


class AlbumPage(models.Model):
    album = models.ForeignKey(Album)
    layout = models.ForeignKey(PageLayout)
    num = models.IntegerField()

    def __unicode__(self):
        count_ = self.photo_set.count()
        return "Page %d of album '%s' with %d photo%s" % (self.num, self.album.name, count_, "s" if count_ != 1 else "")

    class Meta:
        ordering = ('album', 'num',)


class Photo(models.Model):
    page = models.ForeignKey(AlbumPage)
    url = models.URLField()
    num = models.IntegerField()
    caption = models.TextField(blank=True)
    crop_x = models.IntegerField()
    crop_y = models.IntegerField()
    crop_w = models.IntegerField()
    crop_h = models.IntegerField()

    def __unicode__(self):
        desc = self.caption[:16] + "..." if len(self.caption) > 16 else self.caption
        return "Photo %d, page %d, album '%s': %s" % (self.num, self.page.num, self.page.album.name, desc)

    class Meta:
        ordering = ('page', 'num',)
#!/usr/bin/env python
import logging

import django.contrib.auth.models
from django.db import models
from django.db.models import Sum
from django.db.models.query import Q
from .utils import generate_hash

logger = logging.getLogger(__name__)


class Album(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True, default=None,
                               help_text="The parent album of the album, if any")
    owner = models.ForeignKey(django.contrib.auth.models.User, help_text="The owner of the album")
    name = models.CharField(max_length=32, help_text="The name of the album, max. 32 characters")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    share_id = models.CharField(max_length=40, blank=True, null=True, default=generate_hash,
                                editable=False, verbose_name="Share ID")

    def get_num_photos(self):
        """Returns the amount of photos in the album."""
        return Photo.objects.filter(Q(page__album=self)).count()

    def get_max_photos(self):
        """Returns the maximum amount of photos in the album with the current amount and type of pages."""
        return self.albumpage_set.aggregate(Sum('layout__num_photos'))["layout__num_photos__sum"] or 0

    def has_user_access(self, user, share_id=None):
        """Returns whether or not the given user has access to the album with the optionally given share ID."""
        username = user.get_username() if user.is_authenticated() else "Anonymous"
        if user == self.owner:
            logger.info("User %s is the owner of album '%s', access granted", username, self.name)
            return True
        if share_id == self.share_id:
            logger.info("Correct share ID for album '%s', access granted", self.name)
            return True
        logger.info("Denied access to album '%s' to user %s and share ID %s", self.name, username, share_id)

    def __unicode__(self):
        return self.name


class PageLayout(models.Model):
    name = models.CharField(max_length=32, help_text="The name of the page layout", unique=True)
    css_class = models.CharField(max_length=32, help_text="The CSS class used for the page")
    num_photos = models.IntegerField(help_text="The amount of photos per page with this layout")

    def __unicode__(self):
        return self.name


class AlbumPage(models.Model):
    album = models.ForeignKey(Album, help_text="The album this page is part of")
    layout = models.ForeignKey(PageLayout, help_text="The layout of the page")
    num = models.IntegerField(help_text="The page number in the album")

    def __unicode__(self):
        count_ = self.photo_set.count()
        return "Page %d of album '%s' with %d photo%s" % (self.num, self.album.name, count_, "s" if count_ != 1 else "")

    class Meta:
        ordering = ('album', 'num')
        unique_together = ('album', 'num')


class Photo(models.Model):
    page = models.ForeignKey(AlbumPage, help_text="The album page this photo is on")
    url = models.URLField(help_text="The URL of the image on an external service")
    num = models.AutoField(help_text="The number of the photo in the page layout", primary_key=True)
    caption = models.TextField(blank=True, help_text="The optional caption of the image")
    crop_x = models.IntegerField(help_text="The starting X coordinate of the image crop")
    crop_y = models.IntegerField(help_text="The starting Y coordinate of the image crop")
    crop_w = models.IntegerField(help_text="The width of the image crop")
    crop_h = models.IntegerField(help_text="The height of the image crop")

    def __unicode__(self):
        desc = self.caption[:16] + "..." if len(self.caption) > 16 else self.caption
        return "Photo %d, page %d, album '%s': %s" % (self.num, self.page.num, self.page.album.name, desc)

    class Meta:
        ordering = ('page', 'num')
        unique_together = ('page', 'num')
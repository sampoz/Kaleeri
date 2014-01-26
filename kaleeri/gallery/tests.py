#!/usr/bin/env python

from django.contrib.auth.models import User
from django.test import TestCase
from .models import Album, AlbumPage, PageLayout, Photo


class AlbumTest(TestCase):
    fixtures = ["test_data.json"]

    def test_models(self):
        # These are more of sanity checks than actual tests, as we can probably be fairly certain that
        # the values actually match. However, checking these helps if somebody happens to modify the fixture,
        # as get_num_photos() and get_max_photos() both naturally depend on these values.
        album = Album.objects.get(id=1)
        subalbum = Album.objects.get(id=2)
        user = User.objects.get(id=1)
        random_user = User.objects.get(id=2)
        layout = PageLayout.objects.get(id=1)
        album_page = AlbumPage.objects.get(id=1)
        album_photo = Photo.objects.get(id=1)

        self.assertEqual(album.albumpage_set.count(), 4)
        self.assertEqual(subalbum.albumpage_set.count(), 2)

        self.assertEqual(album.get_num_photos(), 16)
        self.assertEqual(album.get_max_photos(), 16)
        self.assertEqual(subalbum.get_num_photos(), 6)
        self.assertEqual(subalbum.get_max_photos(), 8)

        # Very technically this might fail randomly with an astronomically low probability, I suppose.
        self.assertNotEqual(album.share_id, subalbum.share_id)

        self.assertTrue(album.has_user_access(user))
        self.assertFalse(album.has_user_access(random_user))
        self.assertTrue(album.has_user_access(random_user, album.share_id))

        # Just to get a bit prettier coverage percentage :)
        self.assertEquals(unicode(album), u"Test album")
        self.assertEquals(unicode(layout), u"Test layout")
        self.assertEquals(unicode(album_page), u"Page 1 of album 'Test album' with 4 photos")
        self.assertEquals(unicode(album_photo), u"Photo 1, page 1, album 'Test album': ")
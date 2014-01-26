#!/usr/bin/env python

from django.contrib.auth.models import User
from django.test import TestCase
from .models import Album, AlbumPage, PageLayout, Photo


class AlbumTest(TestCase):
    def test_models(self):
        user = User.objects.create(username="TestUser", password="irrelevant", email="test@example.com")
        random_user = User.objects.create(username="TestUser 2", password="irrelevant", email="test@example.com")
        album = Album.objects.create(parent=None, owner=user, name="Test album")
        subalbum = Album.objects.create(parent=album, owner=user, name="Subalbum")
        layout = PageLayout.objects.create(name="Test layout", css_class="layout", num_photos=4)
        album_pages = [AlbumPage.objects.create(album=album, num=i, layout=layout) for i in range(1, 5)]
        subalbum_pages = [AlbumPage.objects.create(album=subalbum, num=i, layout=layout) for i in range(1, 3)]
        album_photos = []
        for page in album_pages:
            for i in range(1, 5):
                album_photos.append(Photo.objects.create(url="http://example.com", num=i, page=page,
                                                         crop_x=0, crop_y=0, crop_w=0, crop_h=0))
        subalbum_photos = []
        for page in subalbum_pages:
            for i in range(1, 4):
                subalbum_photos.append(Photo.objects.create(url="http://example.com", num=i, page=page,
                                                            crop_x=0, crop_y=0, crop_w=0, crop_h=0))

        # These are more of sanity checks than actual tests, as we can probably be fairly certain that
        # the values actually match. However, checking these helps if somebody happens to modify the test,
        # as get_num_photos() and get_max_photos() both naturally depend on these values.
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
        self.assertEquals(unicode(album_pages[0]), u"Page 1 of album 'Test album' with 4 photos")
        self.assertEquals(unicode(album_photos[0]), u"Photo 1, page 1, album 'Test album': ")
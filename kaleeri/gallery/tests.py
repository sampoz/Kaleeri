#!/usr/bin/env python

import json
from django.contrib.auth.models import User
from django.test import TestCase
from gallery.utils import render_to_json
from .models import Album, AlbumPage, PageLayout, Photo


class AlbumTest(TestCase):
    fixtures = ["test_data.json"]
    urls = "kaleeri.urls"

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
        album_photo = Photo.objects.get(pk=1)

        self.assertEqual(album.albumpage_set.count(), 4)
        self.assertEqual(subalbum.albumpage_set.count(), 2)

        self.assertEqual(album.get_num_photos(), 16)
        self.assertEqual(album.get_max_photos(), 16)
        self.assertEqual(subalbum.get_num_photos(), 6)
        self.assertEqual(subalbum.get_max_photos(), 8)

        self.assertNotEqual(album.share_id, subalbum.share_id)

        self.assertTrue(album.has_user_access(user))
        self.assertFalse(album.has_user_access(random_user))
        self.assertTrue(album.has_user_access(random_user, album.share_id))

        # Just to get a bit prettier coverage percentage :)
        self.assertEquals(unicode(album), u"Test album")
        self.assertEquals(unicode(layout), u"Test layout")
        self.assertEquals(unicode(album_page), u"Page 1 of album 'Test album' with 4 photos")
        self.assertEquals(unicode(album_photo), u"Photo 1, page 1, album 'Test album': ")

    def assertJSONError(self, path):
        response = self.client.get(path)
        self.assertTrue("error" in json.loads(response.content))

    def test_views(self):
        # http://www.youtube.com/watch?v=MEEM5aQNXNU
        add_photo_data = {
            "url": "http://example.com/new",
            "crop_x": 0,
            "crop_y": 0,
            "crop_w": 0,
            "crop_h": 0
        }

        # Anonymous homepage
        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, "index.html")
        self.assertEquals(response.content.find('<div id="base-logged-in">'), -1)

        # Anonymous album list
        self.assertJSONError("/album/list/")

        # Anonymous subalbum list
        self.assertJSONError("/album/1/subalbums/")

        # Anonymous album creation
        # TODO: broken self.assertJSONError("/album/create/")

        # Login
        response = self.client.post("/login/", {"username": "TestUser", "password": "irrelevant"})
        self.assertEquals(response.status_code, 302)

        # Authenticated homepage
        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, "index.html")
        self.assertNotEqual(response.content.find('class="logged-in">'), -1)

        # Authenticated album list
        response = self.client.get("/album/list/")
        self.assertJSONEqual(response.content, {
            "albums": [
                {
                    "id": 1,
                    "name": "Test album",
                    "photos": 16,
                    "share_id": "fad201add0c32047f037f46e8a213d0d9213e54a",
                    "subalbums": 1
                }
            ]
        })

        # Authenticated subalbum list
        testalbum_subalbums = {
            "albums": [
                {
                    "id": 2,
                    "name": "Subalbum",
                    "photos": 6,
                    "share_id": "3218478924830f8f5abb927c53771c2282dce554",
                    "subalbums": 0
                }
            ]
        }
        response = self.client.get("/album/1/subalbums/")
        self.assertJSONEqual(response.content, testalbum_subalbums)

        # Available album for the owner
        response = self.client.get("/album/1/")
        self.assertJSONEqual(response.content, {
            "parent": None,
            "id": 1,
            "owner": "TestUser",
            "name": "Test album",
            "created_at": "2014-01-26T10:35:07.767000+00:00",
            "share_id": "fad201add0c32047f037f46e8a213d0d9213e54a",
            "pages": 4,
            "photos": 16,
            "max_photos": 16
        })

        # Available page
        response = self.client.get("/album/1/page/1/")
        self.assertJSONEqual(response.content, {
            "photos": [
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]},
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]},
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]},
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]}
            ]
        })

        # Non-existent page
        self.assertJSONError("/album/1/page/0/")

        # Photo adding to an invalid album
        response = self.client.post("/album/9001/page/1/photo/1/add", add_photo_data)
        self.assertEquals(response.status_code, 404)

        # Working photo adding
        response = self.client.post("/album/1/page/1/photo/1/add", add_photo_data)
        photo = Photo.objects.get(url="http://example.com/new")
        self.assertEquals(photo.num, 1)
        self.assertEquals(photo.page, 1)
        self.assertEquals(photo.album.id, 1)

        # Log out
        response = self.client.get("/logout/")
        self.assertEquals(response.status_code, 302)

        # Photo adding not available when logged out
        response = self.client.post("/album/1/page/1/photo/1/add", add_photo_data)
        self.assertEquals(response.status_code, 403)

        # Album not available when logged out
        self.assertJSONError("/album/2/")

        # Page not available when logged out
        self.assertJSONError("/album/2/page/1/")

        # Available via share ID
        response = self.client.get("/album/2/3218478924830f8f5abb927c53771c2282dce554")
        self.assertJSONEqual(response.content, {
            "parent": {
                "id": 1,
                "name": "Test album"
            },
            "id": 2,
            "owner": "TestUser",
            "name": "Subalbum",
            "created_at": "2014-01-26T10:35:07.770000+00:00",
            "share_id": "3218478924830f8f5abb927c53771c2282dce554",
            "pages": 2,
            "photos": 6,
            "max_photos": 8
        })

        # Subalbums available via share ID
        response = self.client.get("/album/1/subalbums/fad201add0c32047f037f46e8a213d0d9213e54a")
        self.assertJSONEqual(response.content, testalbum_subalbums)

        # Non-existent album
        self.assertJSONError("/album/65536/")

        # Page in non-existent album
        self.assertJSONError("/album/65536/page/1/")

        # Sbubalbums of a non-existent album
        self.assertJSONError("/album/65536/subalbums/")

        # Registration page
        response = self.client.get("/register/")
        self.assertEquals(response.templates[0].name, "registration/register.html")

        # Actual registration
        response = self.client.post(
            "/register/",
            {"username": "Caesar", "password1": "sictransit", "password2": "sictransit"}
        )
        self.assertEquals(response.status_code, 302)

        # Login
        response = self.client.post("/login/", {"username": "Caesar", "password": "sictransit"})
        self.assertEquals(response.status_code, 302)

        # No need to check that the user was created, trust that Django's authentication system works

        # Album creation with invalid data
        # TODO: broken self.assertJSONError("/album/create/")

        # Actual album creation
        # TODO: response = self.client.post("/album/create/", {"name": "Dicta Collectanea"})
        # TODO: self.assertEquals(response.status_code, 200)

        # Check that the album exists
        # TODO: self.assertEquals(Album.objects.filter(name="Dicta Collectanea").count(), 1)

        # Photo adding to another user's album
        response = self.client.post("/album/1/page/1/photo/1/add", add_photo_data)
        self.assertEquals(response.status_code, 403)

        # Profile page
        response = self.client.get("/profile/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "registration/userAccount.html")

    @staticmethod
    @render_to_json()
    def dummy_view(data):
        return data

    def test_utils(self):
        self.assertEquals(self.dummy_view({}).content, "{}")
        data = {"a": 1, "b": 2, "c": {"d": 3, "e": 4}}
        self.assertEquals(json.loads(self.dummy_view(data).content), data)
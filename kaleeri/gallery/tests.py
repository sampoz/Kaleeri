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

    def test_views(self):
        # http://www.youtube.com/watch?v=MEEM5aQNXNU
        # Anonymous homepage
        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, "index.html")
        self.assertEquals(response.content.find('<div id="base-logged-in">'), -1)

        # Anonymous album list
        response = self.client.get("/album/list/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Anonymous subalbum list
        response = self.client.get("/album/1/subalbums/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Login
        response = self.client.post("/login/", {"username": "TestUser", "password": "irrelevant"})
        self.assertEquals(response.status_code, 302)

        # Authenticated homepage
        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, "index.html")
        self.assertNotEqual(response.content.find('<div id="base-logged-in">'), -1)

        # Authenticated album list
        response = self.client.get("/album/list/")
        data = json.loads(response.content)
        self.assertTrue("error" not in data)
        self.assertEquals(data, {
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
        data = json.loads(response.content)
        self.assertTrue("error" not in data)
        self.assertEquals(data, testalbum_subalbums)

        # Available album for the owner
        response = self.client.get("/album/1/")
        data = json.loads(response.content)
        self.assertFalse("error" in data)
        self.assertEquals(data, {
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
        data = json.loads(response.content)
        self.assertFalse("error" in data)
        self.assertEquals(data, {
            "photos": [
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]},
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]},
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]},
                {"url": "http://example.com", "caption": "", "crop": [0, 0, 0, 0]}
            ]
        })

        # Non-existent page
        response = self.client.get("/album/1/page/0/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Log out
        response = self.client.get("/logout/")
        self.assertEquals(response.status_code, 302)

        # Album not available when logged out
        response = self.client.get("/album/2/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Page not available when logged out
        response = self.client.get("/album/2/page/1/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Available via share ID
        response = self.client.get("/album/2/3218478924830f8f5abb927c53771c2282dce554")
        data = json.loads(response.content)
        self.assertFalse("error" in data)
        self.assertEquals(data, {
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
        data = json.loads(response.content)
        self.assertFalse("error" in data)
        self.assertEquals(data, testalbum_subalbums)

        # Non-existent album
        response = self.client.get("/album/65536/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Page in non-existent album
        response = self.client.get("/album/65536/page/1/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

        # Sbubalbums of a non-existent album
        response = self.client.get("/album/65536/subalbums/")
        data = json.loads(response.content)
        self.assertTrue("error" in data)

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

        # Album creation page
        response = self.client.get("/album/create/")
        self.assertEquals(response.templates[0].name, "album/create.html")

        # Actual album creation
        response = self.client.post("/album/create/", {"album_name": "Dicta Collectanea"})
        self.assertEquals(response.status_code, 302)

        # Check that the album exists
        self.assertEquals(Album.objects.filter(name="Dicta Collectanea").count(), 1)

        # Profile page
        response = self.client.get("/profile/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "registration/userAccount.html")

    @render_to_json()
    def dummy_view(self, data):
        return data

    def test_utils(self):
        self.assertEquals(self.dummy_view({}).content, "{}")
        data = {"a": 1, "b": 2, "c": {"d": 3, "e": 4}}
        self.assertEquals(json.loads(self.dummy_view(data).content), data)
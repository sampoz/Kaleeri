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
        album = Album.objects.get(pk=1)
        subalbum = Album.objects.get(pk=2)
        user = User.objects.get(pk=1)
        random_user = User.objects.get(pk=2)
        layout = PageLayout.objects.get(pk=1)
        album_page = AlbumPage.objects.get(pk=1)
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

    def assertJSONError(self, path, data=None):
        if data is not None:
            response = self.client.post(path, data)
        else:
            response = self.client.get(path)
        self.assertTrue("error" in json.loads(response.content))

    def assertJSONRedirect(self, response, path):
        self.assertTrue(json.loads(response.content)["redirect"].endswith(path))

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
        response = self.client.post("/album/create/")
        self.assertRedirects(response, "/login/?next=/album/create/")

        # Anonymous album edit
        self.assertJSONError("/album/1/edit/", {"invalid": "data"})

        # Anonymous page edit
        self.assertJSONError("/album/1/page/1/edit/", {"invalid": "data"})

        # Anonymous photo removal
        self.assertJSONError("/album/1/page/1/photo/1/remove/")

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
                    "subalbums": 1,
                    "preview": "http://example.com"
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
                    "subalbums": 0,
                    "preview": "http://example.com"
                }
            ]
        }
        response = self.client.get("/album/1/subalbums/")
        self.assertJSONEqual(response.content, testalbum_subalbums)

        # Available album for the owner
        response = self.client.get("/album/1/")
        self.assertJSONEqual(response.content, {
            "parent": None,
            "subalbums": [{
                "id": 2,
                "name": "Subalbum"
            }],
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
                {"url": "http://example.com", "caption": "", "do_crop": False, "crop": [0, 0, 0, 0], "num": 1},
                {"url": "http://example.com", "caption": "", "do_crop": False, "crop": [0, 0, 0, 0], "num": 2},
                {"url": "http://example.com", "caption": "", "do_crop": False, "crop": [0, 0, 0, 0], "num": 3},
                {"url": "http://example.com", "caption": "", "do_crop": False, "crop": [0, 0, 0, 0], "num": 4}
            ],
            "layout_class": "layout",
            "max_photos": 4,
            "share_id": "fad201add0c32047f037f46e8a213d0d9213e54a"
        })

        # Non-existent page
        self.assertJSONError("/album/1/page/0/")

        # Photo adding to an invalid album
        self.assertJSONError("/album/9001/page/1/photo/1/add/", add_photo_data)

        # Photo removal from nonexistent album
        self.assertJSONError("/album/9001/page/1/photo/1/remove/")

        # Photo removal from nonexistent page
        self.assertJSONError("/album/1/page/9001/photo/1/remove/")

        # Photo removal from nonexistent slot
        self.assertJSONError("/album/1/page/1/photo/9001/remove/")

        # Changing layout with too many photos
        self.assertJSONError("/album/1/page/1/edit/", {"layout": 2})

        # Working photo removal
        response = self.client.post("/album/1/page/1/photo/1/remove/")
        self.assertJSONRedirect(response, "/#album/1/page/1/")

        # Layout change of a nonexistent album
        self.assertJSONError("/album/9001/page/1/edit/", {"layout": 1})

        # Layout change of a nonexistent page
        self.assertJSONError("/album/1/page/9001/edit/", {"layout": 1})

        # Layout change to a nonexistent layout
        self.assertJSONError("/album/1/page/1/edit/", {"layout": 9001})

        # Layout change with invalid data
        self.assertJSONError("/album/1/page/1/edit/", {"invalid": "data"})

        # Working layout change
        response = self.client.post("/album/1/page/1/edit/", {"layout": 2})
        self.assertJSONRedirect(response, "/#album/1/page/1/")
        page = AlbumPage.objects.get(album__pk=1, num=1)
        self.assertEquals(page.layout.pk, 2)

        # Change back
        response = self.client.post("/album/1/page/1/edit/", {"layout": 1})
        self.assertJSONRedirect(response, "/#album/1/page/1/")
        page = AlbumPage.objects.get(album__pk=1, num=1)
        self.assertEquals(page.layout.pk, 1)

        # Photo adding with invalid data
        self.assertJSONError("/album/1/page/1/photo/1/add/", {"invalid": "data"})

        # Photo adding to out-of-bounds slot
        self.assertJSONError("/album/1/page/1/photo/0/add/", {"url": "http://example.com"})
        self.assertJSONError("/album/1/page/1/photo/9001/add/", {"url": "http://example.com"})

        # Photo replacing
        self.assertJSONError("/album/1/page/1/photo/2/add/", {"url": "http://example.com"})

        # Working photo adding
        response = self.client.post("/album/1/page/1/photo/4/add/", add_photo_data)
        self.assertJSONRedirect(response, "/#album/1/page/1/")
        photo = Photo.objects.get(url="http://example.com/new")
        self.assertEquals(photo.num, 4)
        self.assertEquals(photo.page.num, 1)
        self.assertEquals(photo.page.album.id, 1)

        # Log out
        response = self.client.get("/logout/")
        self.assertEquals(response.status_code, 302)

        # Photo adding not available when logged out
        self.assertJSONError("/album/1/page/1/photo/1/add/", add_photo_data)

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
            "subalbums": None,
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

        # Album creation page
        response = self.client.get("/album/create/")
        self.assertEquals(response.templates[0].name, "album/create.html")

        # Album creation with invalid data
        response = self.client.post("/album/create/", {"invalid": "data"})
        self.assertEquals(response.status_code, 200) # 200 is only returned with invalid or no data

        # Actual album creation
        response = self.client.post("/album/create/", {"name": "Dicta Collectanea", "layout": 1, "parent": ""})
        self.assertEquals(Album.objects.filter(name="Dicta Collectanea").count(), 1)
        album = Album.objects.get(name="Dicta Collectanea")
        self.assertRedirects(response, "/#album/%d/" % album.pk)

        # Renaming a nonexistent album
        self.assertJSONError("/album/9001/edit/", {"invalid": "data"})

        # Album renaming without a new name
        self.assertJSONError("/album/%d/edit/" % album.pk, {"invalid": "data"})

        # Working album renaming
        response = self.client.post("/album/%d/edit/" % album.pk, {"name": "Dicta Collectanea II"})
        self.assertJSONRedirect(response, "/#album/%d/" % album.pk)
        album = Album.objects.get(pk=album.pk)
        self.assertEquals(album.name, "Dicta Collectanea II")

        # Photo adding to another user's album
        self.assertJSONError("/album/1/page/1/photo/1/add/", add_photo_data)

        # Photo removal from another user's album
        self.assertJSONError("/album/1/page/1/photo/1/remove/", add_photo_data)

        # Editing another user's album
        self.assertJSONError("/album/1/edit/", {"name": "Forbidden"})

        # Layout change of another user's album
        self.assertJSONError("/album/1/page/1/edit/", {"layout": 1})

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
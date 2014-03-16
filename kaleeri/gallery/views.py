#!/usr/bin/env python

import logging
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseForbidden
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import AlbumForm
from .forms import PhotoForm
from .models import Album, Photo
from .utils import render_to_json
from models import AlbumPage
from models import PageLayout


logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def home(request):
    return render_to_response('index.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {'form': form})


@render_to_json()
def list_albums(request, parent=None, share_id=None):
    """Returns a list of the logged-in user's albums or the subalbums of the given album."""
    if not request.user.is_authenticated() and not parent and not share_id:
        logger.info("An anonymous user tried to retrieve the list of albums")
        return {"error": "Forbidden"}

    if parent is not None:
        username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"
        try:
            album = Album.objects.get(id=parent)
        except ObjectDoesNotExist:
            logger.info("User %s requested subalbums of a non-existing album: %s", username, parent)
            return {"error": "No such album"}

        if not album.has_user_access(request.user, share_id):
            logger.info("User %s requested subalbums of album %s without access", username, parent)
            return {"error": "Forbidden"}

    if share_id:
        albums = Album.objects.filter(parent=parent)
    else:
        albums = Album.objects.filter(owner=request.user, parent=parent)
    albums = albums.annotate(subalbums=Count('album'))

    return {
        "albums": [
            {
                "id": album.id,
                "name": album.name,
                "photos": album.get_num_photos(),
                "share_id": album.share_id,
                "subalbums": album.subalbums
            } for album in albums
        ]
    }


@render_to_json()
def show_album(request, album_id, share_id=None):
    username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"

    try:
        album = Album.objects.get(id=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s requested a non-existing album: %s", username, album_id)
        return {"error": "No such album"}

    if not album.has_user_access(request.user, share_id):
        logger.info("User %s requested album %s without access", username, album.name)
        return {"error": "Forbidden"}

    return {
        "parent": {
            "id": album.parent.id,
            "name": album.parent.name
        } if album.parent else None,
        "id": album.id,
        "owner": album.owner.get_username(),
        "name": album.name,
        "created_at": album.created_at.isoformat(),
        "share_id": album.share_id,
        "pages": album.albumpage_set.count(),
        "photos": album.get_num_photos(),
        "max_photos": album.get_max_photos()
    }


@render_to_json()
def show_page(request, album_id, page_num, share_id=None):
    username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"
    page_num = int(page_num)

    try:
        album = Album.objects.get(id=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s requested a page in a non-existing album: %s", username, album_id)
        return {"error": "No such album"}

    if not album.has_user_access(request.user, share_id):
        logger.info("User %s requested page from album %s without access", username, album.name)
        return {"error": "Forbidden"}

    try:
        result_page = album.albumpage_set.get(num=page_num)
    except ObjectDoesNotExist:
        logger.info("User %s requested non-existent page %d in album %s", username, page_num, album.name)
        return {"error": "Invalid page"}

    return {
        "photos": [
            {
                "url": photo.url,
                "caption": photo.caption,
                "num": photo.num,
                "crop": [photo.crop_x, photo.crop_y, photo.crop_w, photo.crop_h]
            } for photo in result_page.photo_set.all()
        ],
        "max_photos": result_page.layout.num_photos,
        "layout_class": result_page.layout.css_class,
        "share_id": album.share_id
    }


@login_required
def create_album(request):
    if request.method == 'GET':
        return render_to_response("album/create.html", RequestContext(request))

    form = AlbumForm(request.POST)
    if not form.is_valid():
        logger.info("User %s tried to create album with invalid data", request.user.get_username())
        return render_to_response('album/create.html', {'form': form, 'user': request.user})

    logger.info("Creating album '%s' for user %s", request.POST["name"], request.user.get_username())
    album = form.save(commit=False)
    album.owner = request.user
    album.save()

    # TODO: Is this checked by AlbumForm?
    layout = PageLayout.objects.get(id=request.POST["layout"])

    page = AlbumPage()
    page.layout = layout
    page.album = album
    page.num = 1
    page.save()
    url = request.build_absolute_uri(reverse("home")) + "#album/%d/" % album.pk
    return redirect(url)


@render_to_json()
def edit_album(request, album_id):
    if not request.user.is_authenticated():
        return {"error": "Forbidden"}

    user = request.user.get_username()
    try:
        album = Album.objects.get(pk=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s tried to edit invalid album ID %d", user, int(album_id))
        return {"error": "Invalid album"}

    if not album.has_user_access(request.user):
        logger.info("User %s tried to edit album '%s' belonging to another user", user, album.name)
        return {"error": "Forbidden"}

    # Name is currently the only modifiable property
    if "name" not in request.POST or not request.POST["name"].strip():
        logger.info("User %s tried to edit album '%s' without a new name", user, album.name)
        return {"error": "Missing name"}

    album.name = request.POST["name"]
    album.save()
    logger.info("User %s renamed album ID %d to '%s'", user, album.pk, album.name)
    url = request.build_absolute_uri(reverse("home")) + "#album/%d/" % album.pk
    return {"redirect": url}


@render_to_json()
def edit_page(request, album_id, page_num):
    if not request.user.is_authenticated():
        return {"error": "Forbidden"}

    user = request.user.get_username()
    try:
        album = Album.objects.get(pk=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s tried to edit page %d in a nonexistent album ID %d", user, int(page_num), int(album_id))
        return {"error": "Invalid album"}

    if not album.has_user_access(request.user):
        logger.info("User %s tried to edit page %d in album '%s' belonging to another user",
                    user, int(page_num), album.name)
        return {"error": "Forbidden"}

    try:
        page = AlbumPage.objects.get(pk=page_num)
    except ObjectDoesNotExist:
        logger.info("User %s tried to edit nonexistent page %d in the album '%s'", user, int(page_num), album.name)
        return {"error": "Invalid page"}

    # Layout is the only modifiable property - check if the new layout has less photos than the page currently has
    if "layout" not in request.POST:
        logger.info("User %s tried to edit page %d in album '%s' without a new layout", user, int(page_num), album.name)
        return {"error": "Missing layout"}

    try:
        layout = PageLayout.objects.get(pk=request.POST["layout"])
    except ObjectDoesNotExist:
        logger.info("User %s tried to change page %d in album '%s' to an invalid layout",
                    user, int(page_num), album.name)
        return {"error": "Invalid layout"}

    photo_count = page.photo_set.count()
    if photo_count > layout.num_photos:
        logger.info("User %s tried to change page %d in album '%s' to a too small layout",
                    user, int(page_num), album.name)
        return {"error": "New layout cannot contain all current photos"}

    page.layout = layout
    page.save()

    url = request.build_absolute_uri(reverse("home")) + "#album/%d/page/%d/" % (album.pk, page.num)
    return {"redirect": url}


@render_to_json()
def add_photo(request, album_id, page_num, photo_num):
    if not request.user.is_authenticated():
        return {"error": "Forbidden"}

    user = request.user.get_username()
    try:
        album = Album.objects.get(pk=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s tried to add a photo to the nonexistent album ID %d", user, int(album_id))
        return {"error": "Invalid album"}

    if not album.has_user_access(request.user):
        logger.info("User %s tried to add a photo to the album '%s' owned by another user", user, album.name)
        return {"error": "Forbidden"}

    layout = AlbumPage.objects.get(album=album, num=page_num).layout
    photo_num = int(photo_num)
    if photo_num < 1 or photo_num >= layout.num_photos:
        logger.info("User %s tried to add out-of-bounds photo to slot %d on page %d in album '%s'",
                    user, int(photo_num), int(page_num), album.name)
        return {"error": "Photo number out of bounds"}

    if Photo.objects.filter(num=photo_num, page__num=page_num, page__album__pk=album_id).count() > 0:
        logger.info("User %s tried to replace photo in slot %d on page %d in album '%s'",
                    user, int(photo_num), int(page_num), album.name)
        return {"error": "Already exists"}

    form = PhotoForm(request.POST)
    if not form.is_valid():
        logger.info("User %s tried to add a photo with invalid data", request.user.get_username())
        return {"error": "Invalid data"}

    photo = form.save(commit=False)
    photo.url = request.POST["url"]
    page = AlbumPage.objects.get(album=album, num=page_num)
    photo.album = album
    photo.page = page
    photo.num = int(photo_num)
    photo.save()
    logger.info("User %s added a new photo to album %s, page %d, slot %d: %s",
                request.user.get_username(), album.name, photo.page.num, photo.num, photo.url)

    url = request.build_absolute_uri(reverse('home')) + '#album/%d/page/%d/' % (int(album_id), int(page_num))
    return {"redirect": url}


@render_to_json()
def remove_photo(request, album_id, page_num, photo_num):
    if not request.user.is_authenticated():
        return {"error": "Forbidden"}

    user = request.user.get_username()
    try:
        album = Album.objects.get(pk=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s tried to remove a photo from the nonexistent album ID %d", user, int(album_id))
        return {"error": "Invalid album"}

    if not album.has_user_access(request.user):
        logger.info("User %s tried to remove a photo from the album '%s' owned by another user", user, album.name)
        return {"error": "Forbidden"}

    try:
        page = AlbumPage.objects.get(album=album, num=int(page_num))
    except ObjectDoesNotExist:
        logger.info("User %s tried to remove a photo from the nonexistent page %d in album '%s'",
                    user, int(page_num), album.name)
        return {"error": "Invalid page"}

    try:
        photo = Photo.objects.get(page=page, num=int(photo_num))
    except ObjectDoesNotExist:
        logger.info("User %s tried to remove a photo from the nonexistent slot %d on page %d in album '%s'",
                    user, int(photo_num), int(page_num), album.name)
        return {"error": "Invalid photo"}

    photo.delete()
    url = request.build_absolute_uri(reverse('home')) + '#album/%d/page/%d/' % (int(album_id), int(page_num))
    return {"redirect": url}


@login_required
def user_account(request):
    return render_to_response('registration/userAccount.html', {"user": request.user})
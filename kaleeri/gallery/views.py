#!/usr/bin/env python

import logging
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from .forms import AlbumForm
from .forms import PhotoForm
from .models import Album, Order
from .utils import render_to_json
from models import AlbumPage
from models import PageLayout
import md5

logger = logging.getLogger(__name__)


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
        "layout_class": result_page.layout.css_class
    }


def create_album(request):
    logger.info("new album create started")
    if not request.user.is_authenticated():
        logger.info("Anonymous user tried to create an album")
        return {"error": "Forbidden"}

    if request.method == 'GET':
        return render_to_response("album/create.html", RequestContext(request))

    form = AlbumForm(request.POST)
    if not form.is_valid():
        logger.info("validation errors were " + str(form.errors))
        logger.info("User %s tried to create album with invalid data", request.user.get_username())
        return render_to_response('index.html', {'user': request.user})

    logger.info("Creating album '%s' for user %s", request.POST["name"], request.user.get_username())
    album = form.save(commit=False)
    album.owner = request.user
    album.save()

    page = AlbumPage()
    if PageLayout.objects.count() < 1:
        layout = PageLayout()
        layout.name="start"
        layout.num_photos=3
        layout.save()
    else:
        layout = PageLayout.objects.get(name="start")
    page.layout = layout
    page.album = album
    page.num = 1
    page.save()
    url = request.build_absolute_uri(reverse("home"))
    return redirect(url)


def add_photo(request):
    logger.info(request.path)
    album_number = 0
    if not request.user.is_authenticated():
        logger.info("Anonymous user tried to add photo")
        return {"error": "Forbidden"}

    if request.method == 'GET':
        album_number = request.get("album")
        return render_to_response("add.html", {}, context_instance=RequestContext(request))

    form = PhotoForm(request.POST)

    if not form.is_valid():
        logger.info(str(form.errors))
        return render_to_response("add.html", {'user': request.user, 'errors' : str(form.errors)}, context_instance=RequestContext(request))

    photo = form.save(commit=False)
    photo.url = request.POST["url"]
    photo.album = Album.objects.get(pk=album_number)
    photo.save()
    logger.info("added new photo")
    url = request.build_absolute_uri(reverse("home"))
    return redirect(url)


@login_required
def user_account(request):
    return render_to_response('registration/userAccount.html', {"user": request.user})


@login_required
def order(request):
    secret = "2e187259a15282fee3c9a59343ba87b3"
    sid = "selleri"
    if request.method == "GET":
        order = Order()
        order.album = Album.objects.get(pk=int(request.GET.get("album", "")))
        order.price = 0
        order.save()

        checksumstr = "pid=%s&sid=%s&amount=%s&token=%s"%(order.id, sid, order.price, secret)
        m = md5.new(checksumstr)
        logger.info(checksumstr)
        return render_to_response("order.html", {'payment_id': order.id,
                                          'seller_id': sid,
                                          'success_url': request.build_absolute_uri(),
                                          'cancel_url': request.build_absolute_uri(),
                                          'error_url': request.build_absolute_uri(),
                                          'checksum': m.hexdigest()})


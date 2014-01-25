#!/usr/bin/env python

import logging
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response, render
from .models import Album
from .utils import render_to_json


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
def show_album(request, album_id):
    username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"

    try:
        album = Album.objects.get(id=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s requested a non-existing album: %s", username, album_id)
        return {"error": "No such album"}

    if not album.has_user_access(request.user):
        logger.info("User %s requested album %s without access", username, album.name)
        return {"error": "Forbidden"}

    return {
        "parent": {
            "id": album.parent.id,
            "name": album.parent.name
        } if album.parent else None,
        "owner": album.owner.get_username(),
        "name": album.name,
        "created_at": album.created_at.isoformat(),
        "share_id": album.share_id,
        "pages": album.albumpage_set.count(),
        "photos": album.get_num_photos(),
        "max_photos": album.get_max_photos()
    }


@render_to_json()
def show_page(request, album_id, page_num):
    username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"
    page_num = int(page_num)

    try:
        album = Album.objects.get(id=album_id)
    except ObjectDoesNotExist:
        logger.info("User %s requested a page in a non-existing album: %s", username, album_id)
        return {"error": "No such album"}

    if not album.has_user_access(request.user):
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
                "crop": [photo.crop_x, photo.crop_y, photo.crop_w, photo.crop_h]
            } for photo in result_page.photo_set.all()
        ]
    }

@login_required
def add_album(request):
    if request.method == 'GET':
        return render_to_response('album/create.html')
    elif request.method == 'POST':
        a = Album(name=request.POST.album-name)
        a.save()
        return render_to_response('/')

@login_required
def user_account(request):
    return render_to_response('registration/userAccount.html', {"user": request.user})
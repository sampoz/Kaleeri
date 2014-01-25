#!/usr/bin/env python

import logging
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response, render
from .models import Album
from .utils import render_to_json, missing_keys


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
def album(request):
    if 'album' not in request.GET:
        logging.info("Request for an album missing album ID parameter")


@render_to_json()
def page(request):
    missing = missing_keys(request.GET, ('album', 'page'))
    if not missing:
        logging.info("Request for a page missing parameter(s): %s", missing)
        return {"error": "Invalid request"}

    username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"
    album_id = request.GET['album']
    page_num = request.GET['page']

    try:
        album = Album.objects.get(id=request.GET['album'])
    except ObjectDoesNotExist:
        logging.info("Request for a non-existing album: %s", album_id)
        return {"error": "No such album"}

    if not album.has_user_access(request.user):
        logging.info("User %s requested album %s without access", username, album.name)
        return {"error": "Forbidden"}

    if not 1 < page_num <= album.albumpage_set.count():
        logging.info("User %s requested out-of-bounds page %d in album %s", username, page_num, album.name)
        return {"error": "Invalid page"}

    result_page = album.albumpage_set.get(num=page_num)

    return {
        "photos": [
            {
                "url": photo.url,
                "text": photo.text,
                "crop": [photo.crop_x, photo.crop_y, photo.crop_w, photo.crop_h]
            } for photo in result_page.photo_set.all()
        ]
    }


@login_required
def user_account(request):
    return render_to_response('registration/userAccount.html', {"user": request.user})
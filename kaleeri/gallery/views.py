#!/usr/bin/env python

import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response, render
from .models import Gallery
from .utils import render_to_json, missing_keys


def home(request):
    return render_to_response('index.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {'form': form})


@render_to_json()
def page(request):
    missing = missing_keys(request.GET, ('gallery', 'page'))
    if not missing:
        logging.info("Request for a page missing parameter(s): %s", missing)
        return {"error": "Invalid request"}

    username = request.user.get_username() if request.user.is_authenticated() else "Anonymous"
    gallery_id = request.GET['gallery']
    page_num = request.GET['page']

    try:
        gallery = Gallery.objects.get(id=request.GET['gallery'])
    except ObjectDoesNotExist:
        logging.info("Request for a non-existing gallery: %s", gallery_id)
        return {"error": "No such gallery"}

    if not gallery.has_user_access(request.user):
        logging.info("User %s requested gallery %s without access", username, gallery.name)
        return {"error": "Forbidden"}

    if not 1 < page_num <= gallery.gallerypage_set.count():
        logging.info("User %s requested out-of-bounds page %d in gallery %s", username, page_num, gallery.name)
        return {"error": "Invalid page"}

    result_page = gallery.gallerypage_set.get(num=page_num)

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
def userAccount(request):
    return render_to_response('registration/userAccount.html', {"user": request.user})
#!/usr/bin/env python
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from django.shortcuts import render_to_response, render


def home(request):
    return render_to_response('index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/books/")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
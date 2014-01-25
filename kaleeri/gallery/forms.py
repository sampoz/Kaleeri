__author__ = 'sampoz'

from django import forms

class AlbumForm(forms.Form):
    Name = forms.CharField(max_length=100)

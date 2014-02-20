from django.forms import ModelForm
from models import Album, AlbumPage, Photo


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['parent', 'name']


class AlbumPageForm(ModelForm):
    class Meta:
        model = AlbumPage
        fields = ['album', 'layout', 'num']


class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['page', 'url', 'num', 'caption', 'crop_x', 'crop_y', 'crop_w', 'crop_h']
from django.forms import ModelForm, ModelChoiceField
from models import Album, AlbumPage, Photo, PageLayout


class AlbumForm(ModelForm):
    layout = ModelChoiceField(queryset=PageLayout.objects.all(),
                              help_text="The default layout for pages in this album", required=True)
    class Meta:
        model = Album
        fields = ['name', 'parent']


class AlbumPageForm(ModelForm):
    class Meta:
        model = AlbumPage
        fields = ['album', 'layout', 'num']


class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['url', 'caption', 'crop_x', 'crop_y', 'crop_w', 'crop_h']
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'gallery.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allaccess.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name="Kaleeri Login"),
    url(r'^register/$', 'gallery.views.register', name="Kaleeri Register"),
    url(r'^login/$', 'django.contrib.auth.views.login', name="Kaleeri Login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": "/"}, name="Kaleeri Logout"),
    url(r'^register/$', 'gallery.views.register', name="Kaleeri Register"),
    url(r'^profile/$', 'gallery.views.user_account', name="Kaleeri Profile"),
    url(r'^album/(\d+)/([a-f0-9]{40})?/?$', 'gallery.views.show_album'),
    url(r'^album/(\d+)/page/(\d+)/([a-f0-9]{40})?/?$', 'gallery.views.show_page'),
    url(r'^album/(\d+)/subalbums/([a-f0-9]{40})?/?$', 'gallery.views.list_albums'),
    url(r'^album/list/$', 'gallery.views.list_albums'),
    url(r'^album/create/$', 'gallery.views.create_album'),
    url(r'^add/$', 'gallery.views.add_photo'),
)

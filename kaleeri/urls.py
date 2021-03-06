from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'gallery.views.home', name='home'),
    url(r'^login/$', 'django.contrib.auth.views.login', name="Kaleeri Login"),
    url(r'^register/$', 'gallery.views.register', name="Kaleeri Register"),
    url(r'^login/$', 'django.contrib.auth.views.login', name="Kaleeri Login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": "/"}, name="Kaleeri Logout"),
    url(r'^register/$', 'gallery.views.register', name="Kaleeri Register"),
    url(r'^profile/$', 'gallery.views.user_account', name="Kaleeri Profile"),
    url(r'^album/(\d+)/([a-f0-9]{40})?/?$', 'gallery.views.show_album'),
    url(r'^album/(\d+)/edit/$', 'gallery.views.edit_album'),
    url(r'^album/(\d+)/page/(\d+)/edit/$', 'gallery.views.edit_page'),
    url(r'^album/(\d+)/page/add/(\d+)/$', 'gallery.views.add_page'),
    url(r'^album/(\d+)/page/(\d+)/remove/$', 'gallery.views.remove_page'),
    url(r'^album/(\d+)/page/(\d+)/photo/(\d+)/add/', 'gallery.views.add_photo'),
    url(r'^album/(\d+)/page/(\d+)/photo/(\d+)/remove/', 'gallery.views.remove_photo'),
    url(r'^album/(\d+)/page/(\d+)/([a-f0-9]{40})?/?$', 'gallery.views.show_page'),
    url(r'^album/(\d+)/subalbums/([a-f0-9]{40})?/?$', 'gallery.views.list_albums'),
    url(r'^album/list/$', 'gallery.views.list_albums'),
    url(r'^album/create/$', 'gallery.views.create_album'),
    url(r'^add/$', 'gallery.views.add_photo'),
    url(r'^album/(\d+)/order/$', 'gallery.views.order'),
    url(r'^order/checksum/(\d+)/(\d+)/(\d+)/$', 'gallery.views.order_checksum'),
    url(r'^order/success/$', 'gallery.views.order_success'),
    url(r'^order/cancel/$', 'gallery.views.order_cancel'),
    url(r'^order/error/$', 'gallery.views.order_error'),
    url(r'^layouts/$', 'gallery.views.list_layouts'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allaccess.urls'))
)
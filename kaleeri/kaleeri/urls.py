from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'gallery.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allaccess.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name="Kaleeri Login"),
    url(r'^register/$', 'gallery.views.register', name="Kaleeri Register"),
    url(r'^accounts/profile', 'gallery.views.user_account', name="Kaleeri Profile"),
)

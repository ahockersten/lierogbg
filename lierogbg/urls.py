"""
URL declarations for the application
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include('rankings.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin', include(admin.site.urls)),
    url(r'^about/', include('about.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^hypermeet/', include('hypermeet.urls')),
    url(r'^maps/', include('maps.urls')),
    url(r'^rankings/', include('rankings.urls')),
    url(r'^rules/', include('rules.urls')),
)

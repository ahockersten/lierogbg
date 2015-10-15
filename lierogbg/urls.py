"""
URL declarations for the application
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin', include(admin.site.urls)),

    # URLs handled by React's router. Everything under /app
    url(r'^app', include('index.urls')),
    # Special case: '/' is handled by the app to redirect to /app
    url(r'^$', 'index.views.index'),


    url(r'^about/', include('about.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^hypermeet/', include('hypermeet.urls')),
    url(r'^maps/', include('maps.urls')),
    url(r'^rankings/', include('rankings.urls')),
    url(r'^rules/', include('rules.urls')),
)

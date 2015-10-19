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

    # api
    url(r'^api/rankings', include('rankings.urls')),
)

"""
URLs for maps
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'maps.views',
    url(r'^index\/$', 'index', name="index"),
)


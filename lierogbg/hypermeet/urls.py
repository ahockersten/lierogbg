"""
URLs for about
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'hypermeet.views',
    url(r'^$', 'index', name="index"),
)

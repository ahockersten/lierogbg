"""
URLs for about
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'about.views',
    url(r'^$', 'index', name="index"),
)


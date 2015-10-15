# vim: set fdm=marker fileencoding=utf-8 ts=4 sw=4 expandtab :
# pylint: disable=invalid-name

"""
The Index app - url wrangling.
"""

from django.conf.urls import patterns, url, include

# This catches everything just to forward it to React's router
urlpatterns = patterns(
    'index.views',
    url(r'^.*$', 'index'),
)

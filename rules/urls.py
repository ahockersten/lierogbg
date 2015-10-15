"""
URLs for rules
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'rules.views',
    url(r'^$', 'index', name="index"),
)

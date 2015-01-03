"""
URL declarations for login/logout
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'accounts.views',
    url(r'^\/*$', 'login'),
    url(r'^\/login.*$', 'login'),
    url(r'^\/authenticate$', 'authenticate'),
    url(r'^\/logout$', 'logout'),
)


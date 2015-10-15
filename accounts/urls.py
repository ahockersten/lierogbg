"""
URL declarations for login/logout
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'accounts.views',
    url(r'^login\/$', 'login', name='login'),
    url(r'^authenticate\/$', 'authenticate', name='authenticate'),
    url(r'^logout\/$', 'logout', name='logout'),
)

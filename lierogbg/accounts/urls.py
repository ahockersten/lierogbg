from django.conf.urls import patterns, include, url

urlpatterns = patterns('accounts.views',
    url(r'^\/*$', 'login'),
    url(r'^\/login.*$', 'login'),
    url(r'^\/authenticate$', 'authenticate'),
    url(r'^\/logout$', 'logout'),
)


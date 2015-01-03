from django.conf.urls import patterns, include, url

urlpatterns = patterns('rules.views',
    url(r'^index\/$', 'index', name="index"),
)


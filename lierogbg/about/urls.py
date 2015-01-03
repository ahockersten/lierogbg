from django.conf.urls import patterns, include, url

urlpatterns = patterns('about.views',
    url(r'^index\/$', 'index', name="index"),
)


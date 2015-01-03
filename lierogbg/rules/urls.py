from django.conf.urls import patterns, url

urlpatterns = patterns(
    'rules.views',
    url(r'^index\/$', 'index', name="index"),
)


from django.conf.urls import patterns, include, url

urlpatterns = patterns('index.views',
    url(r'^\/*$', 'index', name="index"),
)


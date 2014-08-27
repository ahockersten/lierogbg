from django.conf.urls import patterns, include, url

urlpatterns = patterns('index.views',
    url(r'^add_game\/$', 'add_game', name="add_game"),
    url(r'^submit_game\/$', 'submit_game', name="submit_game"),
    url(r'^\/*$', 'index', name="index"),
)


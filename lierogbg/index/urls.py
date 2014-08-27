from django.conf.urls import patterns, include, url

urlpatterns = patterns('index.views',
    url(r'^add_game\/$', 'add_game', name="add_game"),
    url(r'^error\/$', 'error', name="error"),
    url(r'^games\/$', 'games', name="games"),
    url(r'^ranking\/$', 'ranking', name="ranking"),
    url(r'^submit_game\/$', 'submit_game', name="submit_game"),
    url(r'^\/*$', 'ranking', name="ranking"),
)


from django.conf.urls import patterns, include, url

urlpatterns = patterns('index.views',
    url(r'^add_game\/$', 'add_game', name="add_game"),
    url(r'^add_tournament\/$', 'add_tournament', name="add_tournament"),
    url(r'^edit_tournament\/(?P<tournament>.*)', 'edit_tournament', name='edit_tournament'),
    url(r'^error\/$', 'error', name="error"),
    url(r'^games\/$', 'games', name="games"),
    url(r'^ranking\/$', 'ranking', name="ranking"),
    url(r'^tournaments\/$', 'tournaments', name="tournaments"),
    url(r'^submit_game\/$', 'submit_game', name="submit_game"),
    url(r'^submit_tournament\/$', 'submit_tournament', name="submit_tournament"),
    url(r'^update_total_ante\/$', 'update_total_ante', name="update_total_ante"),
    url(r'^\/*$', 'ranking', name="ranking"),
)


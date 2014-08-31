from django.conf.urls import patterns, include, url

urlpatterns = patterns('index.views',
    url(r'^add_game\/$', 'add_game', name="add_game"),
    url(r'^add_tournament\/$', 'add_tournament', name="add_tournament"),
    url(r'^edit_tournament\/(?P<tournament_id>.*)', 'edit_tournament', name='edit_tournament'),
    url(r'^error\/$', 'error', name="error"),
    url(r'^games\/$', 'games', name="games"),
    url(r'^get_games_list\/(?P<tournament_id>.*)', 'get_games_list', name="get_games_list"),
    url(r'^ranking\/$', 'ranking', name="ranking"),
    url(r'^save_tournament\/(?P<tournament_id>.*)', 'save_tournament', name="save_tournament"),
    url(r'^submit_game\/$', 'submit_game', name="submit_game"),
    url(r'^submit_game\/(?P<tournament_id>.*)\/(?P<ranked>.*)', 'submit_game', name="submit_game"),
    url(r'^submit_tournament\/$', 'submit_tournament', name="submit_tournament"),
    url(r'^tournaments\/$', 'tournaments', name="tournaments"),
    url(r'^update_total_ante\/$', 'update_total_ante', name="update_total_ante"),
    url(r'^view_tournament\/(?P<tournament_id>.*)', 'view_tournament', name='view_tournament'),
    url(r'^\/*$', 'ranking', name="ranking"),
)


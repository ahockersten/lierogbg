"""
Tests for rankings
"""
import datetime
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.utils import timezone
from django.test import TestCase
from django.test import Client, TestCase, RequestFactory
from rankings.models import Player, Tournament, TournamentPlacingAnte
from rankings.models import PlayedGame, Subgame, PointsChanged
from rankings.views import add_tournament, submit_tournament
from rankings.views import create_player_table, games, ranking
from rankings.views import create_tournament_table, tournaments
from rankings.views import prepare_tournament_context

class TestViews(TestCase):
    """
    Test views
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                   real_name="", ranking_points=500,
                                   pool_points=500, active=True,
                                   comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                   real_name="", ranking_points=1500,
                                   pool_points=0, active=True,
                                   comment="")
        p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                   real_name="", ranking_points=1500,
                                   pool_points=0, active=False,
                                   comment="")
        self.t = Tournament.objects.create(finished=False,
                                           start_time=timezone.now(),
                                           name="Tourney",
                                           ante=0, pool_points=0,
                                           total_ante=0,
                                           comment="")
        self.t.players.add(self.p1, self.p2)
        self.tpa1 = TournamentPlacingAnte.objects.create(tournament=self.t,
                                                         placing=1,
                                                         ante=90,
                                                         player=self.p1)
        self.tpa2 = TournamentPlacingAnte.objects.create(tournament=self.t,
                                                         placing=2,
                                                         ante=10,
                                                         player=self.p2)
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p1,
                                       player_right=self.p2,
                                       winner=self.p1, comment="")
        PlayedGame.objects.create(tournament=None, ranked=True,
                                  start_time=timezone.now(),
                                  player_left=self.p2, player_right=self.p1,
                                  winner=self.p2, comment="")
        g3 = PlayedGame.objects.create(tournament=self.t, ranked=False,
                                       start_time=timezone.now(),
                                       player_left=self.p2,
                                       player_right=self.p1,
                                       winner=self.p2, comment="")
        Subgame.objects.create(parent=g1, map_played="", pl_lives=3,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g1, map_played="", pl_lives=0,
                               pr_lives=3, replay_file=None)
        Subgame.objects.create(parent=g3, map_played="", pl_lives=0,
                               pr_lives=0, replay_file=None)

        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com',
            password='top_secret')

    def test_rankings(self):
        """
        Tests the rankings() output
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = ranking(request, active_only='True')
        self.assertEqual(response.status_code, 200)

        response = ranking(request, active_only='False')
        self.assertEqual(response.status_code, 200)

    def test_create_player_table(self):
        """
        Tests the create_player_table() function.
        """
        active_players = create_player_table(active_only='True')
        self.assertEqual(len(active_players), 2)
        self.assertEqual(active_players[0]['games'], 3)
        self.assertEqual(active_players[1]['games'], 3)
        all_players = create_player_table(active_only='False')
        self.assertEqual(len(all_players), 3)
        self.assertEqual(all_players[0]['games'], 3)
        self.assertEqual(all_players[1]['games'], 0)
        self.assertEqual(all_players[2]['games'], 3)

    def test_games(self):
        """
        Tests the games() output
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = games(request)
        self.assertEqual(response.status_code, 200)

    def test_create_tournament_table(self):
        """
        Tests create_tournament_table()
        """

        tournament_table = create_tournament_table()
        self.assertEquals(tournament_table[0]['pk'], self.t.pk)
        self.assertEquals(tournament_table[0]['start_time'], self.t.start_time)
        self.assertEquals(tournament_table[0]['name'], self.t.name)
        self.assertEquals(tournament_table[0]['winner'], self.t.winner())
        self.assertEquals(tournament_table[0]['players'],
                          len(self.t.players.all()))
        self.assertEquals(tournament_table[0]['games'], len(self.t.games()))
        self.assertEquals(tournament_table[0]['ante'], self.t.ante)
        self.assertEquals(tournament_table[0]['total_ante'],
                          self.t.total_ante)
        self.assertEquals(tournament_table[0]['finished'], self.t.finished)

    def test_tournaments(self):
        """
        Tests the tournaments() output
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = tournaments(request)
        self.assertEqual(response.status_code, 200)

    def test_add_tournament(self):
        """
        Tests the add_tournament view
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = add_tournament(request)
        self.assertEqual(response.status_code, 302)

        request.user = self.user

        response = add_tournament(request)
        self.assertEqual(response.status_code, 200)

    def test_submit_tournament_not_logged_in(self):
        """
        Tests the submit tournament view when malformed
        """
        request = self.factory.post('/accounts/login')
        request.user = AnonymousUser()
        response = submit_tournament(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         '/accounts/login/?next=/accounts/login')

    def test_submit_tournament_no_form(self):
        """
        Tests the submit tournament view when malformed
        """
        request = self.factory.post('/accounts/login')
        request.user = self.user
        response = submit_tournament(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingserror/')

    def test_submit_tournament_correct(self):
        # correct form
        management_form_data = {
            'tournamentplacingante_set-MIN_NUM_FORMS' : '0',
            'tournamentplacingante_set-INITIAL_FORMS' : '0',
            'tournamentplacingante_set-TOTAL_FORMS' : '2',
            'tournamentplacingante_set-MAX_NUM_FORMS' : '1000',
            'tournamentplacingante_set-0-id' : '',
            'tournamentplacingante_set-0-placing' : '1',
            'tournamentplacingante_set-0-ante' : '1',
            'tournamentplacingante_set-0-tournament' : '',
            'tournamentplacingante_set-1-id' : '',
            'tournamentplacingante_set-1-placing' : '2',
            'tournamentplacingante_set-1-ante' : '1',
            'tournamentplacingante_set-1-tournament' : '' }
        form = { 'start_time' : '2014-01-01 07:00',
                 'name' : 'Fools tournament',
                 'players' : [self.p1.pk, self.p2.pk],
                 'ante' : 0, # FIXME what does this do?
                 'pool_points' : 0,
                 'total_ante' : 2 }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_tournament(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingsedit_tournament/2')

    def test_submit_tournament_incorrect_ante(self):
        """
        Tests the submit tournament view
        """
        # correct form with incorrect ante total
        management_form_data = {
            'tournamentplacingante_set-MIN_NUM_FORMS' : '0',
            'tournamentplacingante_set-INITIAL_FORMS' : '0',
            'tournamentplacingante_set-TOTAL_FORMS' : '2',
            'tournamentplacingante_set-MAX_NUM_FORMS' : '1000',
            'tournamentplacingante_set-0-id' : '',
            'tournamentplacingante_set-0-placing' : '1',
            'tournamentplacingante_set-0-ante' : '1',
            'tournamentplacingante_set-0-tournament' : '',
            'tournamentplacingante_set-1-id' : '',
            'tournamentplacingante_set-1-placing' : '2',
            'tournamentplacingante_set-1-ante' : '2',
            'tournamentplacingante_set-1-tournament' : '' }
        form = { 'start_time' : '2014-01-01 07:00',
                 'name' : 'Fools tournament',
                 'players' : [self.p1.pk, self.p2.pk],
                 'ante' : 0, # FIXME what does this do?
                 'pool_points' : 0,
                 'total_ante' : 2 }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_tournament(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingserror/')

class TestViewsNormalMatches(TestCase):
    """
    Test views when there are only normal matches, no tournament matches
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                   real_name="", ranking_points=500,
                                   pool_points=500, active=True,
                                   comment="")
        p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                   real_name="", ranking_points=1500,
                                   pool_points=0, active=True,
                                   comment="")
        p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                   real_name="", ranking_points=1500,
                                   pool_points=0, active=False,
                                   comment="")
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=p1, player_right=p2,
                                       winner=p1, comment="")
        g2 = PlayedGame.objects.create(tournament=None, ranked=True,
                                  start_time=timezone.now(),
                                  player_left=p2, player_right=p1,
                                  winner=p2, comment="")
        Subgame.objects.create(parent=g1, map_played="", pl_lives=3,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g1, map_played="", pl_lives=3,
                               pr_lives=3, replay_file=None)
        Subgame.objects.create(parent=g2, map_played="", pl_lives=0,
                               pr_lives=3, replay_file=None)
        PointsChanged.objects.create(player=p1, game=g1, rp_before=600,
                                     rp_after=500, pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=p2, game=g1, rp_before=1400,
                                     rp_after=1500, pp_before=0, pp_after=0)


        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com',
            password='top_secret')

    def test_games(self):
        """
        Tests the games() output
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = games(request)
        self.assertEqual(response.status_code, 200)

    def test_prepare_tournament_context_invalid_tournament(self):
        """
        prepare_tournament_context() for no tournament
        """
        with self.assertRaises(Tournament.DoesNotExist):
            prepare_tournament_context(None, None)


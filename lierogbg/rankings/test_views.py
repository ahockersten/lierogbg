"""
Tests for rankings
"""
import datetime
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.utils import timezone
from django.test import TestCase
from django.test import Client, TestCase, RequestFactory
from rankings.forms import TournamentEditForm
from rankings.models import Player, Tournament, TournamentPlacingAnte
from rankings.models import PlayedGame, Subgame, PointsChanged
from rankings.views import add_tournament, submit_tournament
from rankings.views import create_player_table, games, ranking
from rankings.views import create_tournament_table, tournaments
from rankings.views import prepare_tournament_context
from rankings.views import edit_tournament, view_tournament

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
        # an inactive player
        self.p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                       real_name="", ranking_points=1500,
                                       pool_points=0, active=False,
                                       comment="")
        # an inactive player
        self.p4 = Player.objects.create(name="Bar Foo", color="#00FFFF",
                                        real_name="", ranking_points=500,
                                        pool_points=500, active=False,
                                        comment="")
        self.t = Tournament.objects.create(finished=False,
                                           start_time=timezone.now(),
                                           name="Tourney",
                                           ante=0, pool_points=0,
                                           total_ante=0,
                                           comment="")
        self.t2 = Tournament.objects.create(finished=True,
                                            start_time=timezone.now(),
                                            name="Tourney",
                                            ante=0, pool_points=0,
                                            total_ante=0,
                                            comment="")
        self.t.players.add(self.p1, self.p2)
        self.tpa11 = TournamentPlacingAnte.objects.create(tournament=self.t,
                                                          placing=1,
                                                          ante=90,
                                                          player=self.p1)
        self.tpa12 = TournamentPlacingAnte.objects.create(tournament=self.t,
                                                          placing=2,
                                                          ante=10,
                                                          player=self.p2)
        self.t2.players.add(self.p2, self.p3)
        self.tpa21 = TournamentPlacingAnte.objects.create(tournament=self.t,
                                                          placing=1,
                                                          ante=40,
                                                          player=self.p2)
        self.tpa22 = TournamentPlacingAnte.objects.create(tournament=self.t,
                                                          placing=2,
                                                          ante=10,
                                                          player=self.p3)
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p1,
                                       player_right=self.p2,
                                       winner=self.p1, comment="")
        g2 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p2,
                                       player_right=self.p1,
                                       winner=self.p2, comment="")
        # a tied game
        g3 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p2,
                                       player_right=self.p1,
                                       winner=None, comment="")
        # played between two inactive players
        g4 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p3,
                                       player_right=self.p4,
                                       winner=self.p4, comment="")
        tg1 = PlayedGame.objects.create(tournament=self.t, ranked=False,
                                        start_time=timezone.now(),
                                        player_left=self.p2,
                                        player_right=self.p1,
                                        winner=self.p1, comment="")
        tg2 = PlayedGame.objects.create(tournament=self.t, ranked=False,
                                        start_time=timezone.now(),
                                        player_left=self.p2,
                                        player_right=self.p3,
                                        winner=self.p2, comment="")
        Subgame.objects.create(parent=g1, map_played="", pl_lives=3,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g1, map_played="", pl_lives=0,
                               pr_lives=2, replay_file=None)
        Subgame.objects.create(parent=g2, map_played="", pl_lives=2,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g3, map_played="", pl_lives=0,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g4, map_played="", pl_lives=0,
                               pr_lives=2, replay_file=None)
        Subgame.objects.create(parent=tg1, map_played="", pl_lives=2,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=tg2, map_played="", pl_lives=2,
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
        self.assertEqual(active_players[0]['games'], 5)
        self.assertEqual(active_players[1]['games'], 4)
        all_players = create_player_table(active_only='False')
        self.assertEqual(len(all_players), 4)
        self.assertEqual(all_players[0]['games'], 5)
        self.assertEqual(all_players[1]['games'], 2)
        self.assertEqual(all_players[2]['games'], 4)
        self.assertEqual(all_players[3]['games'], 1)

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
        self.assertEquals(tournament_table[1]['pk'], self.t.pk)
        self.assertEquals(tournament_table[1]['start_time'], self.t.start_time)
        self.assertEquals(tournament_table[1]['name'], self.t.name)
        self.assertEquals(tournament_table[1]['winner'], self.t.winner())
        self.assertEquals(tournament_table[1]['players'],
                          len(self.t.players.all()))
        self.assertEquals(tournament_table[1]['games'], len(self.t.games()))
        self.assertEquals(tournament_table[1]['ante'], self.t.ante)
        self.assertEquals(tournament_table[1]['total_ante'],
                          self.t.total_ante)
        self.assertEquals(tournament_table[1]['finished'], self.t.finished)

        self.assertEquals(tournament_table[0]['pk'], self.t2.pk)
        self.assertEquals(tournament_table[0]['start_time'], self.t2.start_time)
        self.assertEquals(tournament_table[0]['name'], self.t2.name)
        self.assertEquals(tournament_table[0]['winner'], self.t2.winner())
        self.assertEquals(tournament_table[0]['players'],
                          len(self.t2.players.all()))
        self.assertEquals(tournament_table[0]['games'], len(self.t2.games()))
        self.assertEquals(tournament_table[0]['ante'], self.t2.ante)
        self.assertEquals(tournament_table[0]['total_ante'],
                          self.t2.total_ante)
        self.assertEquals(tournament_table[0]['finished'], self.t2.finished)

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
        self.assertEqual(response.url, '/rankingsedit_tournament/3')

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

    def test_prepare_tournament_context_invalid_tournament(self):
        """
        prepare_tournament_context() for no tournament
        """
        with self.assertRaises(Tournament.DoesNotExist):
            prepare_tournament_context(None, None)

    def test_prepare_tournament_context_valid_tournament_no_form(self):
        """
        prepare_tournament_context() for no form
        """
        with self.assertRaises(TypeError):
            prepare_tournament_context(self.t.pk, None)

    def test_prepare_tournament_context_valid(self):
        """
        prepare_tournament_context() for valid data
        """
        result = prepare_tournament_context(self.t.pk, TournamentEditForm)
        self.assertNotEqual(result, {})

    def test_edit_tournament(self):
        """
        Tests the edit_tournament() output
        """
        request = self.factory.get('/accounts/login')
        request.user = self.user

        response = edit_tournament(request, self.t.pk)
        self.assertEqual(response.status_code, 200)

    def test_view_tournament(self):
        """
        Tests the edit_tournament() output
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = view_tournament(request, self.t.pk)
        self.assertEqual(response.status_code, 200)

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

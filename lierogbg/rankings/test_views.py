"""
Tests for rankings
"""
import datetime
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone
from django.test import TestCase
from django.test import Client, TestCase, RequestFactory
from rankings.models import Player, Tournament, TournamentPlacingAnte
from rankings.models import PlayedGame, Subgame, PointsChanged
from rankings.views import create_player_table, games, ranking

class TestViews(TestCase):
    """
    Test views
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
        t = Tournament.objects.create(finished=True,
                                      start_time=timezone.now(),
                                      name="Tourney",
                                      ante=0, pool_points=0, total_ante=0,
                                      comment="")
        t.players.add(p1, p2)
        TournamentPlacingAnte.objects.create(tournament=t, placing=1,
                                             ante=0, player=p1)
        TournamentPlacingAnte.objects.create(tournament=t, placing=2,
                                             ante=0, player=p2)
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=p1, player_right=p2,
                                       winner=p1, comment="")
        PlayedGame.objects.create(tournament=None, ranked=True,
                                  start_time=timezone.now(),
                                  player_left=p2, player_right=p1,
                                  winner=p2, comment="")
        g3 = PlayedGame.objects.create(tournament=t, ranked=False,
                                       start_time=timezone.now(),
                                       player_left=p2, player_right=p1,
                                       winner=p2, comment="")
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

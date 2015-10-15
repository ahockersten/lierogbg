"""
Tests for rankings models
"""
import datetime
from django.forms import ValidationError
from django.utils import timezone
from django.test import TestCase
from rankings.models import Player, PlayedGame, Subgame, Tournament
from rankings.models import TournamentPlacingAnte, PointsChanged


class TestPlayer(TestCase):
    """
    Tests the Player model
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                   real_name="", start_ranking_points=500,
                                   start_pool_points=500, active=True,
                                   comment="")
        p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                   real_name="", start_ranking_points=1500,
                                   start_pool_points=0, active=True,
                                   comment="")
        t = Tournament.objects.create(finished=True,
                                      start_time=timezone.now(),
                                      name="Tourney",
                                      ante=0, pool_points=0, total_ante=0,
                                      comment="")
        t.players.add(p1, p2)
        TournamentPlacingAnte.objects.create(tournament=t, placing=1,
                                             ante=0, player=p1)
        TournamentPlacingAnte.objects.create(tournament=t, placing=1,
                                             ante=0, player=p2)
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=p1, player_right=p2,
                                       winner=p1, comment="")
        PlayedGame.objects.create(tournament=None, ranked=False,
                                  start_time=timezone.now(),
                                  player_left=p2, player_right=p1,
                                  winner=p2, comment="")
        g3 = PlayedGame.objects.create(tournament=t, ranked=False,
                                       start_time=timezone.now(),
                                       player_left=p2, player_right=p1,
                                       winner=p2, comment="")
        Subgame.objects.create(parent=g1, map_played="", pl_lives=0,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g1, map_played="", pl_lives=0,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g3, map_played="", pl_lives=0,
                               pr_lives=0, replay_file=None)

    def test_all_games(self):
        """
        all_games() works
        """
        self.assertEqual(len(Player.objects.get(name="Foo Bar").all_games()),
                         3)

    def test_player_ranked_and_tournament_games(self):
        """
        ranked_and_tournament_games() works
        """
        foobar = Player.objects.get(name="Foo Bar")
        this_year = datetime.datetime(datetime.datetime.today().year, 1, 1)
        next_year = datetime.datetime(this_year.year + 1, 1, 1)
        # All matches occur this year, so this should return all of them
        self.assertEqual(
            len(foobar.ranked_and_tournament_games(since=this_year)), 2)
        # This should return no matches
        self.assertEqual(
            len(foobar.ranked_and_tournament_games(since=next_year)), 0)

    def test_tournament_games(self):
        """
        games() for Tournament works
        """
        self.assertEqual(len(Tournament.objects.get(name="Tourney").games()),
                         1)

    def test_tournament_winner(self):
        """
        Tournament winner is correct
        """
        self.assertEqual(Tournament.objects.get(name="Tourney").winner(),
                         Player.objects.get(name="Foo Bar"))

    def test_find_tpas(self):
        """
        tournament_placing_antes() works
        """
        tourney = Tournament.objects.get(name="Tourney")
        self.assertEqual(len(tourney.tournament_placing_antes()), 2)

    def test_subgames(self):
        """
        subgames() works
        """
        g3 = Tournament.objects.get(name="Tourney").games()[0]
        self.assertEqual(len(g3.subgames()), 1)

class TestPlayerAnteCalculation(TestCase):
    """
    Tests for Player's ante calculation.
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        Player.objects.create(name="Foo Bar", color="#00FF00", real_name="",
                              start_ranking_points=500, start_pool_points=500,
                              active=True, comment="")
        Player.objects.create(name="Bar Baz", color="#FF0000", real_name="",
                              start_ranking_points=1500, start_pool_points=0, active=True,
                              comment="")
        Player.objects.create(name="Baz Qux", color="#0000FF", real_name="",
                              start_ranking_points=2095, start_pool_points=0, active=True,
                              comment="")
        Player.objects.create(name="Inactive", color="#000000", real_name="",
                              start_ranking_points=1900, start_pool_points=0,
                              active=False, comment="")
        Player.objects.create(name="No RP no PP", color="#00AA00",
                              real_name="", start_ranking_points=0, start_pool_points=0,
                              active=True, comment="")
        Player.objects.create(name="No RP some PP", color="#00BB00",
                              real_name="", start_ranking_points=0, start_pool_points=500,
                              active=True, comment="")
        Player.objects.create(name="No RP minimal PP", color="#00BB00",
                              real_name="", start_ranking_points=0, start_pool_points=5,
                              active=True, comment="")

    def test_setup(self):
        """
        Tests that the setup works correctly
        """
        self.assertEqual(len(Player.objects.all()), 7)

    def test_active_players(self):
        """
        Tests active_players()
        """
        self.assertEqual(len(Player.objects.active_players()), 6)

    def test_calculate_ante_percentage_less_pp_1(self):
        """
        Calculate ante for a player with less pool points than they have.
        """
        foobar = Player.objects.get(name="Foo Bar")
        calculated_ante = foobar.calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 28)
        self.assertEqual(calculated_ante["rp"], 530)
        self.assertEqual(calculated_ante["pp"], 470)

    def test_calculate_ante_percentage_no_pp(self):
        """
        Calculate ante for a player for a player with no pool points.
        """
        barbaz = Player.objects.get(name="Bar Baz")
        calculated_ante = barbaz.calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 225)
        self.assertEqual(calculated_ante["rp"], 1500)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_more_pp(self):
        """
        Calculate ante for a player with more pool points than they have.
        """
        foobar = Player.objects.get(name="Foo Bar")
        calculated_ante = foobar.calculate_ante_percentage(10, 700)
        self.assertEqual(calculated_ante["ante"], 100)
        self.assertEqual(calculated_ante["rp"], 1000)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_more_pp_no_pp(self):
        """
        Calculate ante for a player for a player with no pool points when the
        pool point bonus is really large.
        """
        barbaz = Player.objects.get(name="Bar Baz")
        calculated_ante = barbaz.calculate_ante_percentage(10, 700)
        self.assertEqual(calculated_ante["ante"], 225)
        self.assertEqual(calculated_ante["rp"], 1500)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_using_all_same_as_using_more(self):
        """
        Using up all pool points should be the same as using up a lot more.
        """
        foobar = Player.objects.get(name="Foo Bar")
        self.assertEqual(foobar.calculate_ante_percentage(10, 500),
                         foobar.calculate_ante_percentage(10, 1000))

    def test_calculate_ante_percentage_no_rp_no_pp_no_ante(self):
        """
        No RP and no PP means no ante.
        """
        norpnopp = Player.objects.get(name="No RP no PP")
        calculated_ante = norpnopp.calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 0)
        self.assertEqual(calculated_ante["rp"], 0)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_no_rp_some_pp_means_ante(self):
        """
        No RP but some PP means at least 1 ante.
        """
        norpsomepp = Player.objects.get(name="No RP some PP")
        calculated_ante = norpsomepp.calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 30)
        self.assertEqual(calculated_ante["pp"], 470)

    def test_calculate_ante_percentage_at_least_one_ante(self):
        """
        Always at least 1 ante.
        """
        norpminpp = Player.objects.get(name="No RP minimal PP")
        calculated_ante = norpminpp.calculate_ante_percentage(10, 1)
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 1)
        self.assertEqual(calculated_ante["pp"], 4)

    def test_calculate_ante_ranked_less_pp(self):
        """
        Calculate ante for a player with less pool points than they have.
        """
        foobar = Player.objects.get(name="Foo Bar")
        calculated_ante = foobar.calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 6)
        self.assertEqual(calculated_ante["rp"], 540)
        self.assertEqual(calculated_ante["pp"], 460)

    def test_calculate_ranked_ante_no_pp(self):
        """
        Calculate ante for a player for a player with no pool points.
        """
        barbaz = Player.objects.get(name="Bar Baz")
        calculated_ante = barbaz.calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 45)
        self.assertEqual(calculated_ante["rp"], 1500)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ranked_ante_not_modifying_object(self):
        """
        Calculate_ranked_ante() should not modify the object
        """
        foobar = Player.objects.get(name="Foo Bar")
        self.assertEqual(foobar.calculate_ranked_ante(),
                         foobar.calculate_ranked_ante())

    def test_calculate_ranked_ante_more_pp(self):
        """
        Calculate ante for a player with more pool points than they have.
        """
        norpminpp = Player.objects.get(name="No RP minimal PP")
        calculated_ante = norpminpp.calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 5)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ranked_ante_no_rp_no_pp_no_ante(self):
        """
        No RP and no PP means no ante.
        """
        norpnopp = Player.objects.get(name="No RP no PP")
        calculated_ante = norpnopp.calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 0)
        self.assertEqual(calculated_ante["rp"], 0)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ranked_ante_no_rp_some_pp_means_ante(self):
        """
        No RP but some PP means at least 1 ante.
        """
        norpsomepp = Player.objects.get(name="No RP some PP")
        calculated_ante = norpsomepp.calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 40)
        self.assertEqual(calculated_ante["pp"], 460)

# pylint: disable=too-many-instance-attributes
class TestTournament(TestCase):
    """
    Tests related to Tournament
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="", start_ranking_points=500,
                                        start_pool_points=500, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        # an inactive player
        self.p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=False,
                                        comment="")
        # an inactive player
        self.p4 = Player.objects.create(name="Bar Foo", color="#00FFFF",
                                        real_name="", start_ranking_points=500,
                                        start_pool_points=500, active=False,
                                        comment="")
        self.t = Tournament.objects.create(finished=False,
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
        PointsChanged.objects.create(player=self.p1, tournament=self.t,
                                     rp_before=500, rp_after=500,
                                     pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p2, tournament=self.t,
                                     rp_before=500, rp_after=500,
                                     pp_before=0, pp_after=0)
        self.t2 = Tournament.objects.create(finished=True,
                                            start_time=timezone.now(),
                                            name="Tourney",
                                            ante=5, pool_points=0,
                                            total_ante=50,
                                            comment="")
        self.t2.players.add(self.p2, self.p3)
        self.tpa21 = TournamentPlacingAnte.objects.create(tournament=self.t2,
                                                          placing=1,
                                                          ante=40,
                                                          player=self.p2)
        self.tpa22 = TournamentPlacingAnte.objects.create(tournament=self.t2,
                                                          placing=2,
                                                          ante=10,
                                                          player=self.p3)
        PointsChanged.objects.create(player=self.p2, tournament=self.t2,
                                     rp_before=485, rp_after=500,
                                     pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p3, tournament=self.t2,
                                     rp_before=515, rp_after=500,
                                     pp_before=500, pp_after=500)
        self.t3 = Tournament.objects.create(finished=False,
                                            start_time=timezone.now(),
                                            name="Tourney",
                                            ante=5, pool_points=0,
                                            total_ante=50,
                                            comment="")
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
        self.tg1 = PlayedGame.objects.create(tournament=self.t, ranked=False,
                                             start_time=timezone.now(),
                                             player_left=self.p2,
                                             player_right=self.p1,
                                             winner=self.p1, comment="")
        self.tg2 = PlayedGame.objects.create(tournament=self.t, ranked=False,
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
        Subgame.objects.create(parent=self.tg1, map_played="", pl_lives=2,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=self.tg2, map_played="", pl_lives=2,
                               pr_lives=0, replay_file=None)

    def test_distribute_points_open_tournament(self):
        """
        distribute_points() for an open tournament should fail
        """
        with self.assertRaises(ValueError):
            self.t.distribute_points()

    def test_distribute_points_closed_tournament(self):
        """
        distribute_points() for a closed tournament should succeed
        """
        p2_rp_before = self.p2.ranking_points
        p3_rp_before = self.p3.ranking_points
        self.t2.distribute_points()
        # ranking points should have changed now
        # both are greater since they had already "paid in" to the tournament
        # before
        self.assertGreater(Player.objects.get(id=self.p2.pk).ranking_points,
                           p2_rp_before)
        self.assertGreater(Player.objects.get(id=self.p3.pk).ranking_points,
                           p3_rp_before)

    def test_games(self):
        """
        games() works correctly
        """
        self.assertEqual(list(self.t.games()), [self.tg1, self.tg2])
        self.assertEqual(list(self.t2.games()), [])

    def test_winner(self):
        """
        winner() works correctly
        """
        self.assertEqual(self.t.winner(), self.p1)
        self.assertEqual(self.t2.winner(), self.p2)
        self.assertEqual(self.t3.winner(), None)

    def test_tournament_placing_antes(self):
        """
        tournament_placing_antes() works correctly
        """
        self.assertEqual(list(self.t.tournament_placing_antes()),
                         [self.tpa11, self.tpa12])
        self.assertEqual(list(self.t2.tournament_placing_antes()),
                         [self.tpa21, self.tpa22])

    def test_str(self):
        """
        __str__() for Tournament
        """
        self.assertEqual(
            "Tourney_False_{}_0_0_0".format(str(self.t.start_time)),
            str(self.t))

class TestTournamentPlacingAnte(TestCase):
    """
    Tests related to TournamentPlacingAnte
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="", start_ranking_points=500,
                                        start_pool_points=500, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        self.t = Tournament.objects.create(finished=False,
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
    def test_str(self):
        """
        __str__() works correctly
        """
        self.assertEqual("{} 1 90 {}".format(str(self.t), str(self.p1)),
                         str(self.tpa11))

class TestPlayedGame(TestCase):
    """
    Tests related to PlayedGame
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="", start_ranking_points=500,
                                        start_pool_points=500, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        self.g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                            start_time=timezone.now(),
                                            player_left=self.p1,
                                            player_right=self.p2,
                                            winner=self.p1, comment="")
        self.g2 = PlayedGame.objects.create(
            tournament=None, ranked=True,
            start_time=timezone.now() + datetime.timedelta(days=1),
            player_left=self.p2,
            player_right=self.p1,
            winner=self.p2, comment="")
        self.sg11 = Subgame.objects.create(parent=self.g1, map_played="",
                                           pl_lives=3, pr_lives=0,
                                           replay_file=None)
        self.sg12 = Subgame.objects.create(parent=self.g1, map_played="",
                                           pl_lives=0, pr_lives=2,
                                           replay_file=None)
        self.sg21 = Subgame.objects.create(parent=self.g2, map_played="",
                                           pl_lives=2, pr_lives=0,
                                           replay_file=None)

    def test_last_game(self):
        """
        last_game() works correctly
        """
        self.assertEqual(PlayedGame.objects.last_game(), self.g2)

    def test_subgames(self):
        """
        subgames() works correctly
        """
        self.assertEqual(list(self.g1.subgames()), [self.sg11, self.sg12])
        self.assertEqual(list(self.g2.subgames()), [self.sg21])

    def test_str(self):
        """
        __str__() works correctly
        """
        self.assertEqual("{} {} vs {}, (ranked) {} won".format(str(self.g1.start_time),
                                                      str(self.p1),
                                                      str(self.p2),
                                                      str(self.p1)),
                         str(self.g1))

class TestSubgame(TestCase):
    """
    Tests related to Subgame
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="", start_ranking_points=500,
                                        start_pool_points=500, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        self.g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                            start_time=timezone.now(),
                                            player_left=self.p1,
                                            player_right=self.p2,
                                            winner=self.p1, comment="")
        self.g2 = PlayedGame.objects.create(
            tournament=None, ranked=True,
            start_time=timezone.now() + datetime.timedelta(days=1),
            player_left=self.p2,
            player_right=self.p1,
            winner=self.p2, comment="")
        self.sg11 = Subgame.objects.create(parent=self.g1, map_played="",
                                           pl_lives=3, pr_lives=0,
                                           replay_file=None)
        self.sg12 = Subgame.objects.create(parent=self.g1, map_played="",
                                           pl_lives=0, pr_lives=2,
                                           replay_file=None)
        self.sg21 = Subgame.objects.create(parent=self.g2, map_played="",
                                           pl_lives=2, pr_lives=0,
                                           replay_file=None)
    def test_str(self):
        """
        __str__() works correctly
        """
        self.assertEqual("3 - 0", str(self.sg11))
        self.assertEqual("0 - 2", str(self.sg12))
        self.assertEqual("2 - 0", str(self.sg21))

    def test_clean(self):
        """
        The clean() function works.
        """
        # these three are well-formed and should have no problems
        self.sg11.clean()
        self.sg12.clean()
        self.sg21.clean()

        sg4 = Subgame.objects.create(parent=self.g1, map_played="",
                                     pl_lives=-1, pr_lives=0,
                                     replay_file=None)
        sg5 = Subgame.objects.create(parent=self.g1, map_played="",
                                     pl_lives=0, pr_lives=-1,
                                     replay_file=None)
        with self.assertRaises(ValidationError):
            sg4.clean()
        with self.assertRaises(ValidationError):
            sg5.clean()

# pylint: disable=too-many-instance-attributes
class TestPointsChanged(TestCase):
    """
    Tests related to PointsChanged
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="", start_ranking_points=500,
                                        start_pool_points=500, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        self.t = Tournament.objects.create(finished=False,
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
        self.pc1 = PointsChanged.objects.create(
            player=self.p1, tournament=self.t, rp_before=500, rp_after=500,
            pp_before=0, pp_after=0)
        self.pc2 = PointsChanged.objects.create(
            player=self.p2, tournament=self.t, rp_before=500, rp_after=500,
            pp_before=0, pp_after=0)
        self.tg1 = PlayedGame.objects.create(tournament=self.t, ranked=False,
                                             start_time=timezone.now(),
                                             player_left=self.p2,
                                             player_right=self.p1,
                                             winner=self.p1, comment="")
        self.tg2 = PlayedGame.objects.create(tournament=self.t, ranked=False,
                                             start_time=timezone.now(),
                                             player_left=self.p2,
                                             player_right=self.p1,
                                             winner=self.p2, comment="")
        Subgame.objects.create(parent=self.tg1, map_played="", pl_lives=2,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=self.tg2, map_played="", pl_lives=2,
                               pr_lives=0, replay_file=None)

    def test_str(self):
        """
        __str__() works correctly
        """
        self.assertEqual("{}_{}_None_500_500_0_0".format(str(self.p1),
                                                         self.t),
                         str(self.pc1))

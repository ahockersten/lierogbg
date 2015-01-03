from django.utils import timezone
from django.test import TestCase
from models import Player, PlayedGame, Subgame, Tournament, TournamentPlacingAnte

class TestSimpleLookups(TestCase):
    def setUp(self):
        p1 = Player.objects.create(name="Foo Bar", color="#00FF00", real_name="",
                                   ranking_points=500, pool_points=500, active=True,
                                   comment="")
        p2 = Player.objects.create(name="Bar Baz", color="#FF0000", real_name="",
                                   ranking_points=1500, pool_points=0, active=True,
                                   comment="")
        t = Tournament.objects.create(finished=True, start_time=timezone.now(),
                                      name="Tourney",
                                      ante=0, pool_points=0, total_ante=0, comment="")
        t.players.add(p1, p2)
        tpa1 = TournamentPlacingAnte.objects.create(tournament=t, placing=1, ante=0,
                                                    player=p1)
        tpa2 = TournamentPlacingAnte.objects.create(tournament=t, placing=1, ante=0,
                                                    player=p2)
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=p1, player_right=p2,
                                       winner=p1, comment="")
        g2 = PlayedGame.objects.create(tournament=None, ranked=False,
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

    def test_player_all_games(self):
        self.assertEqual(len(Player.objects.get(name="Foo Bar").all_games()),
                         3)

    def test_player_ranked_and_tournament_games(self):
        self.assertEqual(len(Player.objects.get(name="Foo Bar").ranked_and_tournament_games()),
                         2)

    def test_tournament_games(self):
        self.assertEqual(len(Tournament.objects.get(name="Tourney").games()),
                         1)

    def test_tournament_winner(self):
        self.assertEqual(Tournament.objects.get(name="Tourney").winner(),
                         Player.objects.get(name="Foo Bar"))

    def test_find_tpas(self):
        self.assertEqual(len(Tournament.objects.get(name="Tourney").tournament_placing_antes()),
                         2)

    def test_subgames(self):
        g3 = Tournament.objects.get(name="Tourney").games()[0]
        self.assertEqual(len(g3.subgames()), 1)

class TestAnteCalculation(TestCase):
    def setUp(self):
        Player.objects.create(name="Foo Bar", color="#00FF00", real_name="",
                              ranking_points=500, pool_points=500, active=True,
                              comment="")
        Player.objects.create(name="Bar Baz", color="#FF0000", real_name="",
                              ranking_points=1500, pool_points=0, active=True,
                              comment="")
        Player.objects.create(name="Baz Qux", color="#0000FF", real_name="",
                              ranking_points=2095, pool_points=0, active=True,
                              comment="")
        Player.objects.create(name="Inactive", color="#000000", real_name="",
                              ranking_points=1900, pool_points=0, active=False,
                              comment="")
        Player.objects.create(name="No RP no PP", color="#00AA00", real_name="",
                              ranking_points=0, pool_points=0, active=True,
                              comment="")
        Player.objects.create(name="No RP some PP", color="#00BB00", real_name="",
                              ranking_points=0, pool_points=500, active=True,
                              comment="")
        Player.objects.create(name="No RP minimal PP", color="#00BB00", real_name="",
                              ranking_points=0, pool_points=5, active=True,
                              comment="")

    def test_setup(self):
        self.assertEqual(len(Player.objects.all()), 7)

    def test_active_players(self):
        self.assertEqual(len(Player.objects.active_players()), 6)

    def test_calculate_ante_percentage_less_pp_1(self):
        # calculate ante for a player with less pool points than they have
        calculated_ante = Player.objects.get(name="Foo Bar").calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 28)
        self.assertEqual(calculated_ante["rp"], 530)
        self.assertEqual(calculated_ante["pp"], 470)

    def test_calculate_ante_percentage_no_pp(self):
        # calculate ante for a player for a player with no pool points
        calculated_ante = Player.objects.get(name="Bar Baz").calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 225)
        self.assertEqual(calculated_ante["rp"], 1500)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_more_pp(self):
        # calculate ante for a player with more pool points than they have
        calculated_ante = Player.objects.get(name="Foo Bar").calculate_ante_percentage(10, 700)
        self.assertEqual(calculated_ante["ante"], 100)
        self.assertEqual(calculated_ante["rp"], 1000)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_more_pp_no_pp(self):
        # calculate ante for a player for a player with no pool points when the pool point
        # bonus is really large
        calculated_ante = Player.objects.get(name="Bar Baz").calculate_ante_percentage(10, 700)
        self.assertEqual(calculated_ante["ante"], 225)
        self.assertEqual(calculated_ante["rp"], 1500)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_using_all_same_as_using_more(self):
        # using up all pool points should be the same as using up a lot more
        self.assertEqual(Player.objects.get(name="Foo Bar").calculate_ante_percentage(10, 500),
                         Player.objects.get(name="Foo Bar").calculate_ante_percentage(10, 1000))

    def test_calculate_ante_percentage_no_rp_no_pp_no_ante(self):
        # no RP and no PP means no ante
        calculated_ante = Player.objects.get(name="No RP no PP").calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 0)
        self.assertEqual(calculated_ante["rp"], 0)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ante_percentage_no_rp_some_pp_means_ante(self):
        # no RP but some PP means at least 1 ante
        calculated_ante = Player.objects.get(name="No RP some PP").calculate_ante_percentage(10, 30)
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 30)
        self.assertEqual(calculated_ante["pp"], 470)

    def test_calculate_ante_percentage_at_least_one_ante(self):
        # always at least 1 ante
        calculated_ante = Player.objects.get(name="No RP minimal PP").calculate_ante_percentage(10, 1)
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 1)
        self.assertEqual(calculated_ante["pp"], 4)

    def test_calculate_ante_ranked_less_pp(self):
        # calculate ante for a player with less pool points than they have
        calculated_ante = Player.objects.get(name="Foo Bar").calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 6)
        self.assertEqual(calculated_ante["rp"], 540)
        self.assertEqual(calculated_ante["pp"], 460)

    def test_calculate_ranked_ante_no_pp(self):
        # calculate ante for a player for a player with no pool points
        calculated_ante = Player.objects.get(name="Bar Baz").calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 45)
        self.assertEqual(calculated_ante["rp"], 1500)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ranked_ante_not_modifying_object(self):
        # calculate_ranked_ante() should not modify the object
        self.assertEqual(Player.objects.get(name="Foo Bar").calculate_ranked_ante(),
                         Player.objects.get(name="Foo Bar").calculate_ranked_ante())

    def test_calculate_ranked_ante_more_pp(self):
        # calculate ante for a player with more pool points than they have
        calculated_ante = Player.objects.get(name="No RP minimal PP").calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 5)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ranked_ante_no_rp_no_pp_no_ante(self):
        # no RP and no PP means no ante
        calculated_ante = Player.objects.get(name="No RP no PP").calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 0)
        self.assertEqual(calculated_ante["rp"], 0)
        self.assertEqual(calculated_ante["pp"], 0)

    def test_calculate_ranked_ante_no_rp_some_pp_means_ante(self):
        # no RP but some PP means at least 1 ante
        calculated_ante = Player.objects.get(name="No RP some PP").calculate_ranked_ante()
        self.assertEqual(calculated_ante["ante"], 1)
        self.assertEqual(calculated_ante["rp"], 40)
        self.assertEqual(calculated_ante["pp"], 460)

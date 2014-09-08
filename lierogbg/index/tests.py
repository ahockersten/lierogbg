from django.test import TestCase
from models import Player

class TestPlayer(TestCase):
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

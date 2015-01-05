"""
Tests for rankings
"""
import datetime
from django.contrib.auth.models import User, AnonymousUser
from django.forms import ValidationError
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
from rankings.views import edit_tournament, view_tournament, save_tournament
from rankings.views import add_game, submit_game

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
                                            ante=0, pool_points=0,
                                            total_ante=0,
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
        self.assertEqual(tournament_table[1]['pk'], self.t.pk)
        self.assertEqual(tournament_table[1]['start_time'], self.t.start_time)
        self.assertEqual(tournament_table[1]['name'], self.t.name)
        self.assertEqual(tournament_table[1]['winner'], self.t.winner())
        self.assertEqual(tournament_table[1]['players'],
                          len(self.t.players.all()))
        self.assertEqual(tournament_table[1]['games'], len(self.t.games()))
        self.assertEqual(tournament_table[1]['ante'], self.t.ante)
        self.assertEqual(tournament_table[1]['total_ante'],
                          self.t.total_ante)
        self.assertEqual(tournament_table[1]['finished'], self.t.finished)

        self.assertEqual(tournament_table[0]['pk'], self.t2.pk)
        self.assertEqual(tournament_table[0]['start_time'], self.t2.start_time)
        self.assertEqual(tournament_table[0]['name'], self.t2.name)
        self.assertEqual(tournament_table[0]['winner'], self.t2.winner())
        self.assertEqual(tournament_table[0]['players'],
                          len(self.t2.players.all()))
        self.assertEqual(tournament_table[0]['games'], len(self.t2.games()))
        self.assertEqual(tournament_table[0]['ante'], self.t2.ante)
        self.assertEqual(tournament_table[0]['total_ante'],
                          self.t2.total_ante)
        self.assertEqual(tournament_table[0]['finished'], self.t2.finished)

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
        """
        Submit tournament, with a correct form
        """
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
        Submit tournament, correct form with incorrect ante total
        """
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
        The edit_tournament() output
        """
        request = self.factory.get('/accounts/login')
        request.user = self.user

        response = edit_tournament(request, self.t.pk)
        self.assertEqual(response.status_code, 200)

    def test_view_tournament(self):
        """
        The view_tournament() output
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = view_tournament(request, self.t.pk)
        self.assertEqual(response.status_code, 200)

    def test_save_tournament_valid_finish(self):
        """
        Saving a tournament for a valid case, which is now finished
        """
        management_form_data = {
            'tournamentplacingante_set-MIN_NUM_FORMS' : '0',
            'tournamentplacingante_set-INITIAL_FORMS' : '0',
            'tournamentplacingante_set-TOTAL_FORMS' : '2',
            'tournamentplacingante_set-MAX_NUM_FORMS' : '1000',
            'tournamentplacingante_set-0-id' : self.tpa11.pk,
            'tournamentplacingante_set-0-placing' : self.tpa11.placing,
            'tournamentplacingante_set-0-ante' : self.tpa11.ante,
            'tournamentplacingante_set-0-tournament' : self.t.pk,
            'tournamentplacingante_set-0-player' : self.p1.pk,
            'tournamentplacingante_set-1-id' : self.tpa12.pk,
            'tournamentplacingante_set-1-placing' : self.tpa12.placing,
            'tournamentplacingante_set-1-ante' : self.tpa12.ante,
            'tournamentplacingante_set-1-tournament' : self.t.pk,
            'tournamentplacingante_set-1-player' : self.p2.pk,
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'name' : 'Fools tournament',
            'players' : [self.p1.pk, self.p2.pk],
            'ante' : 100, # FIXME what does this do?
            'pool_points' : 0,
            'total_ante' : 100,
            'finished' : 'True',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = save_tournament(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingstournaments/')

    def test_save_tournament_valid(self):
        """
        Saving a tournament for a valid case.
        """
        management_form_data = {
            'tournamentplacingante_set-MIN_NUM_FORMS' : '0',
            'tournamentplacingante_set-INITIAL_FORMS' : '0',
            'tournamentplacingante_set-TOTAL_FORMS' : '2',
            'tournamentplacingante_set-MAX_NUM_FORMS' : '1000',
            'tournamentplacingante_set-0-id' : self.tpa11.pk,
            'tournamentplacingante_set-0-placing' : self.tpa11.placing,
            'tournamentplacingante_set-0-ante' : self.tpa11.ante,
            'tournamentplacingante_set-0-tournament' : self.t.pk,
            'tournamentplacingante_set-1-id' : self.tpa12.pk,
            'tournamentplacingante_set-1-placing' : self.tpa12.placing,
            'tournamentplacingante_set-1-ante' : self.tpa12.ante,
            'tournamentplacingante_set-1-tournament' : self.t.pk
            }
        form = { 'start_time' : '2014-01-01 07:00',
                 'name' : 'Fools tournament',
                 'players' : [self.p1.pk, self.p2.pk],
                 'ante' : 100, # FIXME what does this do?
                 'pool_points' : 0,
                 'total_ante' : 100 }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = save_tournament(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingstournaments/')

    def test_save_tournament_already_finished(self):
        """
        Saving a tournament that has already finished fails.
        """
        # correct form with incorrect ante total
        management_form_data = {
            'tournamentplacingante_set-MIN_NUM_FORMS' : '0',
            'tournamentplacingante_set-INITIAL_FORMS' : '0',
            'tournamentplacingante_set-TOTAL_FORMS' : '2',
            'tournamentplacingante_set-MAX_NUM_FORMS' : '1000',
            'tournamentplacingante_set-0-id' : self.tpa21.pk,
            'tournamentplacingante_set-0-placing' : self.tpa21.placing,
            'tournamentplacingante_set-0-ante' : self.tpa21.ante,
            'tournamentplacingante_set-0-tournament' : self.t2.pk,
            'tournamentplacingante_set-1-id' : self.tpa22.pk,
            'tournamentplacingante_set-1-placing' : self.tpa22.placing,
            'tournamentplacingante_set-1-ante' : self.tpa22.ante,
            'tournamentplacingante_set-1-tournament' : self.t2.pk
            }
        form = { 'start_time' : '2014-01-01 07:00',
                 'name' : 'Fools tournament',
                 'players' : [self.p2.pk, self.p3.pk],
                 'ante' : 50, # FIXME what does this do?
                 'pool_points' : 0,
                 'total_ante' : 50 }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = save_tournament(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingserror/')

    def test_save_tournament_no_mgmt_form(self):
        """
        Saving a tournament with no management form fails.
        This testcase will be obsolete in Django 1.8, see
        https://code.djangoproject.com/ticket/22276
        """
        # no management form data
        management_form_data = {
            'tournamentplacingante_set-0-id' : self.tpa21.pk,
            'tournamentplacingante_set-0-placing' : self.tpa21.placing,
            'tournamentplacingante_set-0-ante' : self.tpa21.ante,
            'tournamentplacingante_set-0-tournament' : self.t2.pk,
            'tournamentplacingante_set-1-id' : self.tpa22.pk,
            'tournamentplacingante_set-1-placing' : self.tpa22.placing,
            'tournamentplacingante_set-1-ante' : self.tpa22.ante,
            'tournamentplacingante_set-1-tournament' : self.t2.pk
            }
        form = { 'start_time' : '2014-01-01 07:00',
                 'name' : 'Fools tournament',
                 'players' : [self.p2.pk, self.p3.pk],
                 'ante' : 50, # FIXME what does this do?
                 'pool_points' : 0,
                 'total_ante' : 50 }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        with self.assertRaises(ValidationError):
            save_tournament(request, tournament_id=self.t.pk)

    def test_save_tournament_invalid_form(self):
        """
        Saving a tournament with an invalid form fails
        """
        # no management form data
        management_form_data = {
            'tournamentplacingante_set-MIN_NUM_FORMS' : '0',
            'tournamentplacingante_set-INITIAL_FORMS' : '0',
            'tournamentplacingante_set-TOTAL_FORMS' : '2',
            'tournamentplacingante_set-MAX_NUM_FORMS' : '1000',
            'tournamentplacingante_set-0-id' : self.tpa21.pk,
            'tournamentplacingante_set-0-placing' : self.tpa21.placing,
            'tournamentplacingante_set-0-ante' : self.tpa21.ante,
            'tournamentplacingante_set-0-tournament' : self.t2.pk,
            'tournamentplacingante_set-1-id' : self.tpa22.pk,
            'tournamentplacingante_set-1-placing' : self.tpa22.placing,
            'tournamentplacingante_set-1-ante' : self.tpa22.ante,
            'tournamentplacingante_set-1-tournament' : self.t2.pk
            }
        form = {  }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = save_tournament(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)

    def test_submit_game_valid_tournament(self):
        """
        Submit a game for a valid tournament case.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p1.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings')

        # an unranked game means ranking points should not have changed
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_tournament_already_finished(self):
        """
        Submit a game for a tournament that has already finished
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p1.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=self.t2.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingserror/')

        # an unranked game means ranking points should not have changed
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

class TestViewsNormalMatches(TestCase):
    """
    Test views when there are only normal matches, no tournament matches
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
        self.p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                   real_name="", ranking_points=1500,
                                   pool_points=0, active=False,
                                   comment="")
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p1, player_right=self.p2,
                                       winner=self.p1, comment="")
        g2 = PlayedGame.objects.create(tournament=None, ranked=True,
                                  start_time=timezone.now(),
                                  player_left=self.p2, player_right=self.p1,
                                  winner=self.p2, comment="")
        Subgame.objects.create(parent=g1, map_played="", pl_lives=3,
                               pr_lives=0, replay_file=None)
        Subgame.objects.create(parent=g1, map_played="", pl_lives=3,
                               pr_lives=3, replay_file=None)
        Subgame.objects.create(parent=g2, map_played="", pl_lives=0,
                               pr_lives=3, replay_file=None)
        PointsChanged.objects.create(player=self.p1, game=g1, rp_before=600,
                                     rp_after=500, pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p2, game=g1, rp_before=1400,
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

    def test_add_game(self):
        """
        add_game() works
        """
        request = self.factory.get('/accounts/login')
        request.user = self.user

        response = add_game(request)
        self.assertEqual(response.status_code, 200)

    def test_add_game(self):
        """
        add_game() doesn't work for anonymous user
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = add_game(request)
        self.assertEqual(response.status_code, 302)

    def test_submit_game_valid(self):
        """
        Submit a game for a valid case.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p1.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings')

        # a ranked game means ranking points should have changed
        self.assertGreater(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertLess(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_valid_unranked(self):
        """
        Submit a game for a valid unranked case.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p1.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings')

        # an unranked game means ranking points should not have changed
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_no_mgmt_form(self):
        """
        Submit a game with no management form
        This testcase will be obsolete in Django 1.8, see
        https://code.djangoproject.com/ticket/22276
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p1.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        with self.assertRaises(ValidationError):
            submit_game(request, tournament_id=None)

        # error means no change
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)

    def test_submit_game_invalid(self):
        """
        Submit a game for an invalid case. This game's winner is different
        than the participants.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        p3_rp_before = self.p3.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p3.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingserror/')

        # error means no change
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)
        self.assertEqual(Player.objects.get(id=self.p3.pk).ranking_points,
                         p3_rp_before)

    def test_submit_game_tied(self):
        """
        Submit a game for tied case. This game's winner is different
        than the participants.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        p3_rp_before = self.p3.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '3',
            'subgame_set-0-pr_lives' : '0',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : '',
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings')

        # a ranked game means ranking points should have changed, even in a
        # tie, since p1 had less RP than p2
        self.assertGreater(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertLess(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_broken_formset(self):
        """
        Submit a game for broken formset.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        p3_rp_before = self.p3.ranking_points
        # remaining lives are < 0, which is an error
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Foo',
            'subgame_set-0-pl_lives' : '-1',
            'subgame_set-0-pr_lives' : '-1',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p1.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankingserror/')

        # error means no change
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)
        self.assertEqual(Player.objects.get(id=self.p3.pk).ranking_points,
                         p3_rp_before)

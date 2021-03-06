"""
Tests for rankings views
"""
from django.contrib.auth.models import User, AnonymousUser
from django.forms import ValidationError
from django.http import Http404
from django.utils import timezone
from django.test import TestCase, RequestFactory
from rankings.forms import TournamentEditForm
from rankings.models import Player, Tournament, TournamentPlacingAnte
from rankings.models import PlayedGame, Subgame, PointsChanged
from rankings.views import add_tournament, submit_tournament
from rankings.views import create_player_table, games, ranking
from rankings.views import create_tournament_table, tournaments
from rankings.views import prepare_tournament_context
from rankings.views import edit_tournament, view_tournament, save_tournament
from rankings.views import add_game, submit_game, update_total_ante
from rankings.views import get_games_list, get_players_list, error
from rankings.views import get_tournament_games_list, internal_info
import datetime
import random


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class TestViews(TestCase):
    """
    Test views
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
                                        real_name="",
                                        start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        # an inactive player
        self.p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                        real_name="",
                                        start_ranking_points=1500,
                                        start_pool_points=0, active=False,
                                        comment="")
        # an inactive player
        self.p4 = Player.objects.create(name="Bar Foo", color="#00FFFF",
                                        real_name="",
                                        start_ranking_points=500,
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
        PointsChanged.objects.create(player=self.p1, game=g1,
                                     rp_before=500, rp_after=515,
                                     pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p2, game=g1,
                                     rp_before=500, rp_after=485,
                                     pp_before=0, pp_after=0)
        g2 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p2,
                                       player_right=self.p1,
                                       winner=self.p2, comment="")
        PointsChanged.objects.create(player=self.p1, game=g2,
                                     rp_before=515, rp_after=500,
                                     pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p2, game=g2,
                                     rp_before=485, rp_after=500,
                                     pp_before=0, pp_after=0)
        # a tied game
        g3 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p2,
                                       player_right=self.p1,
                                       winner=None, comment="")
        PointsChanged.objects.create(player=self.p1, game=g3,
                                     rp_before=500, rp_after=500,
                                     pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p2, game=g3,
                                     rp_before=500, rp_after=500,
                                     pp_before=0, pp_after=0)
        # played between two inactive players
        g4 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=timezone.now(),
                                       player_left=self.p3,
                                       player_right=self.p4,
                                       winner=self.p4, comment="")
        PointsChanged.objects.create(player=self.p3, game=g4,
                                     rp_before=500, rp_after=485,
                                     pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p4, game=g4,
                                     rp_before=500, rp_after=515,
                                     pp_before=0, pp_after=0)
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
        self.assertEqual(all_players[0]['games'], 1)
        self.assertEqual(all_players[1]['games'], 5)
        self.assertEqual(all_players[2]['games'], 4)
        self.assertEqual(all_players[3]['games'], 2)

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
        self.assertEqual(tournament_table[0]['start_time'],
                         self.t2.start_time)
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
        self.assertEqual(response.url, '/rankings/error/')

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
            'tournamentplacingante_set-1-tournament' : ''
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'name' : 'Fools tournament',
            'players' : [self.p1.pk, self.p2.pk],
            'ante' : 0, # FIXME what does this do?
            'pool_points' : 0,
            'total_ante' : 2
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_tournament(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/edit_tournament/3')

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
            'tournamentplacingante_set-1-tournament' : ''
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'name' : 'Fools tournament',
            'players' : [self.p1.pk, self.p2.pk],
            'ante' : 0, # FIXME what does this do?
            'pool_points' : 0,
            'total_ante' : 2
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_tournament(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/error/')

    def test_prepare_tournament_context_invalid_tournament(self):
        """
        prepare_tournament_context() for no tournament
        """
        # pylint: disable=no-member
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

    def test_edit_tournament_invalid(self):
        """
        The edit_tournament() output on invalid data
        """
        request = self.factory.get('/accounts/login')
        request.user = self.user

        response = edit_tournament(request, '')
        self.assertEqual(response.status_code, 302)

    def test_edit_tournament(self):
        """
        The edit_tournament() output
        """
        request = self.factory.get('/accounts/login')
        request.user = self.user

        response = edit_tournament(request, self.t.pk)
        self.assertEqual(response.status_code, 200)

    def test_view_tournament_invalid(self):
        """
        The view_tournament() output on invalid data
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()

        response = view_tournament(request, '')
        self.assertEqual(response.status_code, 302)

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
        self.assertEqual(response.url, '/rankings/tournaments/')

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
        form = {
            'start_time' : '2014-01-01 07:00',
            'name' : 'Fools tournament',
            'players' : [self.p1.pk, self.p2.pk],
            'ante' : 100, # FIXME what does this do?
            'pool_points' : 0,
            'total_ante' : 100
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = save_tournament(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/tournaments/')

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
        form = {
            'start_time' : '2014-01-01 07:00',
            'name' : 'Fools tournament',
            'players' : [self.p2.pk, self.p3.pk],
            'ante' : 50, # FIXME what does this do?
            'pool_points' : 0,
            'total_ante' : 50
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = save_tournament(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/error/')

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
        form = {
            'start_time' : '2014-01-01 07:00',
            'name' : 'Fools tournament',
            'players' : [self.p2.pk, self.p3.pk],
            'ante' : 50, # FIXME what does this do?
            'pool_points' : 0,
            'total_ante' : 50
            }
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
        form = {}
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
        self.assertEqual(response.url, '/rankings/')

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
        self.assertEqual(response.url, '/rankings/error/')

        # an unranked game means ranking points should not have changed
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)

    def test_get_players_list_no_ajax(self):
        """
        get_players_list() that is not AJAX fails
        """
        form = {
            }
        request = self.factory.get('/accounts/login', data=form)
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            get_players_list(request)

    def test_get_players_list_valid_all_time(self):
        """
        get_players_list() for valid all time data
        """
        form = {
            'all_time' : 'True',
            'active_only' : 'True'
            }
        request = self.factory.get('/accounts/login', data=form,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = get_players_list(request)
        self.assertEqual(response.status_code, 200)

    def test_get_players_list_valid_not_all_time(self):
        """
        get_players_list() for valid data, not all time
        """
        form = {
            'all_time' : 'False',
            'active_only' : 'False'
            }
        request = self.factory.get('/accounts/login', data=form,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = get_players_list(request)
        self.assertEqual(response.status_code, 200)

    def test_get_tournament_games_list(self):
        """
        get_tournament_games_list() when a tournament is supplied
        """
        form = {
            }
        request = self.factory.get('/accounts/login', data=form,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = get_tournament_games_list(request, tournament_id=self.t.pk)
        self.assertEqual(response.status_code, 200)

class TestViewsNormalMatches(TestCase):
    """
    Test views when there are only normal matches, no tournament matches
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
        self.p3 = Player.objects.create(name="Qux Quux", color="#0000FF",
                                        real_name="", start_ranking_points=1500,
                                        start_pool_points=0, active=False,
                                        comment="")
        g1 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=datetime.date(2010, 1, 1),
                                       player_left=self.p1,
                                       player_right=self.p2, winner=self.p1,
                                       comment="")
        g2 = PlayedGame.objects.create(tournament=None, ranked=True,
                                       start_time=datetime.date(2010, 1, 2),
                                       player_left=self.p2,
                                       player_right=self.p1, winner=self.p2,
                                       comment="")
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
        PointsChanged.objects.create(player=self.p1, game=g2, rp_before=500,
                                     rp_after=400, pp_before=0, pp_after=0)
        PointsChanged.objects.create(player=self.p2, game=g2, rp_before=1500,
                                     rp_after=1600, pp_before=0, pp_after=0)

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

    def test_add_game_anonymous(self):
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
        self.assertEqual(response.url, '/rankings/')

        # a ranked game means ranking points should have changed
        self.assertGreater(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertLess(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_valid_2(self):
        """
        Submit a game for a valid case, where the other player wins
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '0',
            'subgame_set-0-pr_lives' : '3',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : self.p2.pk,
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/')

        # a ranked game means ranking points should have changed
        # both increase due to PP being unlocked
        self.assertLess(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertGreater(Player.objects.get(id=self.p2.pk).ranking_points,
                           p2_rp_before)

    def test_submit_game_valid_ajax(self):
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
        request = self.factory.post('/accounts/login', data=form,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.url, '/rankings/')

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
        self.assertEqual(response.url, '/rankings/error/')

        # error means no change
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)
        self.assertEqual(Player.objects.get(id=self.p3.pk).ranking_points,
                         p3_rp_before)

    def test_submit_game_invalid_played_game_form(self):
        """
        Submit a game for an invalid played game form.
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
        # no start_date included
        form = {
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
        self.assertEqual(response.url, '/rankings/error/')

        # error means no change
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)
        self.assertEqual(Player.objects.get(id=self.p3.pk).ranking_points,
                         p3_rp_before)

    def test_submit_game_ied(self):
        """
        Submit a game for tied case.
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
        self.assertEqual(response.url, '/rankings/')

        # a ranked game means ranking points should have changed, even in a
        # tie, since p1 had less RP than p2
        self.assertGreater(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertLess(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_proper_tie(self):
        """
        Submit a game for tied case where the number of lives per subgame are
        also tied.
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
            'subgame_set-0-pr_lives' : '3',
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
        self.assertEqual(response.url, '/rankings/')

        # a ranked game means ranking points should have changed, even in a
        # tie, since p1 had less RP than p2
        self.assertGreater(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertLess(Player.objects.get(id=self.p2.pk).ranking_points,
                        p2_rp_before)

    def test_submit_game_proper_tie_2(self):
        """
        Submit a game for tied case where the number of lives per subgame are
        also tied. This tests with the reverse order of players to the first
        test.
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
            'subgame_set-0-pr_lives' : '3',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'winner' : '',
            'player_left' : self.p2.pk,
            'player_right' : self.p1.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/')

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
        self.assertEqual(response.url, '/rankings/error/')

        # error means no change
        self.assertEqual(Player.objects.get(id=self.p1.pk).ranking_points,
                         p1_rp_before)
        self.assertEqual(Player.objects.get(id=self.p2.pk).ranking_points,
                         p2_rp_before)
        self.assertEqual(Player.objects.get(id=self.p3.pk).ranking_points,
                         p3_rp_before)

class TestViewsSimilarPlayers(TestCase):
    """
    Test views for two very similar players
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="", start_ranking_points=1000,
                                        start_pool_points=29, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="", start_ranking_points=1000,
                                        start_pool_points=0, active=True,
                                        comment="")
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com',
            password='top_secret')

    def test_submit_game_valid(self):
        """
        Submit a game for a valid case with two similar players. This makes
        sure to test some edge cases in the code that are not touched
        by other test code.
        """
        p1_rp_before = self.p1.ranking_points
        p2_rp_before = self.p2.ranking_points
        management_form_data = {
            'subgame_set-MIN_NUM_FORMS' : '0',
            'subgame_set-INITIAL_FORMS' : '0',
            'subgame_set-TOTAL_FORMS' : '1',
            'subgame_set-MAX_NUM_FORMS' : '1000',
            'subgame_set-0-map' : 'Mmmap',
            'subgame_set-0-pl_lives' : '0',
            'subgame_set-0-pr_lives' : '3',
            'subgame_set-0-replay_file' : '',
            }
        form = {
            'start_time' : '2014-01-01 07:00',
            'player_left' : self.p1.pk,
            'player_right' : self.p2.pk,
            'ranked' : 'on',
            }
        form.update(management_form_data)
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        response = submit_game(request, tournament_id=None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/rankings/')

        # a ranked game means ranking points should have changed
        self.assertGreater(Player.objects.get(id=self.p1.pk).ranking_points,
                           p1_rp_before)
        self.assertGreater(Player.objects.get(id=self.p2.pk).ranking_points,
                           p2_rp_before)

    def test_update_total_ante_no_ajax(self):
        """
        update_total_ante() that is not AJAX fails
        """
        form = {
            'ante' : '10',
            'players' : [self.p1.pk, self.p2.pk],
            'pool_points' : '10'
            }
        request = self.factory.post('/accounts/login', data=form)
        request.user = self.user
        with self.assertRaises(Http404):
            update_total_ante(request)

    def test_update_total_ante_simple(self):
        """
        update_total_ante(), simple case
        """
        form = {
            'ante' : '10',
            'players' : [self.p1.pk, self.p2.pk],
            'pool_points' : '10'
            }
        request = self.factory.post('/accounts/login', data=form,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = update_total_ante(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'202')

    def test_update_total_ante_invalid(self):
        """
        update_total_ante(), invalid case
        """
        form = {
            'ante' : '10',
            'players' : [self.p1.pk, self.p2.pk],
            'pool_points' : 'a'
            }
        request = self.factory.post('/accounts/login', data=form,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = update_total_ante(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Error')

class TestViewsLotsOfMatches(TestCase):
    """
    Test view with *lots* of games
    """
    def setUp(self):
        """
        Creates a huge amount of games
        """
        self.p1 = Player.objects.create(name="Foo Bar", color="#00FF00",
                                        real_name="",
                                        start_ranking_points=500,
                                        start_pool_points=500, active=True,
                                        comment="")
        self.p2 = Player.objects.create(name="Bar Baz", color="#FF0000",
                                        real_name="",
                                        start_ranking_points=1500,
                                        start_pool_points=0, active=True,
                                        comment="")
        i = 0
        while i < 100:
            winner = random.choice([self.p1, self.p2])
            p1_rp = self.p1.ranking_points
            p2_rp = self.p2.ranking_points
            g = PlayedGame.objects.create(tournament=None, ranked=True,
                                          start_time=timezone.now(),
                                          player_left=self.p1,
                                          player_right=self.p2,
                                          winner=winner, comment="")
            Subgame.objects.create(parent=g, map_played="", pl_lives=3,
                                   pr_lives=0, replay_file=None)
            if winner == self.p1:
                PointsChanged.objects.create(
                    player=self.p1, game=g,
                    rp_before=p1_rp, rp_after=p1_rp + 10,
                    pp_before=0, pp_after=0)
                PointsChanged.objects.create(
                    player=self.p2, game=g,
                    rp_before=p2_rp, rp_after=p2_rp - 10,
                    pp_before=0, pp_after=0)
            else:
                PointsChanged.objects.create(
                    player=self.p1, game=g,
                    rp_before=p1_rp, rp_after=p1_rp - 10,
                    pp_before=0, pp_after=0)
                PointsChanged.objects.create(
                    player=self.p2, game=g,
                    rp_before=p2_rp, rp_after=p2_rp + 10,
                    pp_before=0, pp_after=0)
            i = i + 1

        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com',
            password='top_secret')

    def test_get_games_list_no_ajax(self):
        """
        get_games_list() that is not AJAX fails
        """
        form = {
            }
        request = self.factory.get('/accounts/login', data=form)
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            get_games_list(request)

    def test_get_tournament_games_list_no_ajax(self):
        """
        get_tournament_games_list() that is not AJAX fails
        """
        form = {
            }
        request = self.factory.get('/accounts/login', data=form)
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            get_tournament_games_list(request, tournament_id=None)

    def test_get_games_list(self):
        """
        get_games_list() for a valid request
        """
        form = {
            'games' : '60',
            'show_all' : 'False',
            }
        request = self.factory.get('/accounts/login', data=form,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = get_games_list(request)
        self.assertEqual(response.status_code, 200)

    def test_get_games_list_no_games(self):
        """
        get_games_list() when no games are supplied
        """
        form = {
            'show_all' : 'True',
            }
        request = self.factory.get('/accounts/login', data=form,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = get_games_list(request)
        self.assertEqual(response.status_code, 200)

    def test_get_tournament_games_list_no_tournament(self):
        """
        get_tournament_games_list() when no tournament is supplied
        """
        form = {
            'show_all' : 'True',
            }
        request = self.factory.get('/accounts/login', data=form,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = get_tournament_games_list(request, tournament_id=None)
        self.assertEqual(response.status_code, 200)

    def test_error(self):
        """
        Error page is rendered correctly.
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()
        response = error(request)
        self.assertEqual(response.status_code, 200)

    def test_internal_info(self):
        """
        Internal info page is rendered correctly.
        """
        request = self.factory.get('/accounts/login')
        request.user = AnonymousUser()
        response = internal_info(request)
        self.assertEqual(response.status_code, 200)

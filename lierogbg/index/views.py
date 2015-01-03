##
# @module index
# @file views.py
#

import datetime
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _
from functools import partial, wraps
from index.models import PlayedGame, PlayedGameForm
from index.models import Player
from index.models import PointsChanged
from index.models import SubgameFormSet
from index.models import Tournament, TournamentCreateForm, TournamentEditForm
from index.models import TournamentPlacingAnte, TournamentPlacingAnteFormSet, TournamentPlacingAnteSubmitForm, TournamentPlacingAnteSubmitFormSet

def about(request):
    return render(request, 'index/about.html')

def rules(request):
    return render(request, 'index/rules.html')

def maps(request):
    return render(request, 'index/maps.html')

def ranking(request, active_only):
    last_game_time = None
    last_game = PlayedGame.objects.last_game()
    if last_game != None:
        last_game_time = last_game.start_time.isoformat()
    context = {
        'players' : create_player_table(active_only),
        'last_game_time' : last_game_time,
    }

    return render(request, 'index/ranking.html', context)

def create_player_table(active_only,
        since=datetime.datetime(datetime.datetime.today().year, 1, 1)):
    shown_players = Player.objects.active_players() if active_only == 'True' else Player.objects.all()
    player_list = shown_players.order_by('ranking_points').reverse()
    players = []
    current_rank = 1
    for p in player_list:
        tmp = {}
        tmp["player"] = p
        tmp["current_rank"] = current_rank
        ranked_and_tournament_games = p.ranked_and_tournament_games(
                                          since=since)
        tmp["round_wins"] = 0
        tmp["round_losses"] = 0
        tmp["round_ties"] = 0
        tmp["rounds"] = 0
        tmp["games"] = len(ranked_and_tournament_games)
        lives = 0
        for g in ranked_and_tournament_games:
            for s in g.subgames():
                if g.player_left == p:
                    lives = lives + s.pl_lives
                    lives = lives - s.pr_lives
                    if s.pl_lives > s.pr_lives:
                        tmp["round_wins"] = tmp["round_wins"] + 1
                    elif s.pl_lives < s.pr_lives:
                        tmp["round_losses"] = tmp["round_losses"] + 1
                    else:
                        tmp["round_ties"] = tmp["round_ties"] + 1
                else:
                    lives = lives - s.pl_lives
                    lives = lives + s.pr_lives
                    if s.pr_lives > s.pl_lives:
                        tmp["round_wins"] = tmp["round_wins"] + 1
                    elif s.pr_lives < s.pl_lives:
                        tmp["round_losses"] = tmp["round_losses"] + 1
                    else:
                        tmp["round_ties"] = tmp["round_ties"] + 1
                tmp["rounds"] = tmp["rounds"] + 1
        tmp["lives"] = lives
        players.append(tmp)
        current_rank = current_rank + 1
    return players

def games(request):
    all_games_by_date = PlayedGame.objects.all().order_by('start_time').reverse()
    last_game = PlayedGame.objects.last_game()
    last_game_time = None
    if last_game != None:
        last_game_time = last_game.start_time.isoformat()
    context = {
        'games' : create_games_table(all_games_by_date),
        'last_game_time' : last_game_time,
    }
    return render(request, 'index/games.html', context)

def create_games_table(games_list):
    games = []
    for g in games_list:
        tmp = {}
        tmp["game"] = g
        tmp["winner"] = _('Tied') if g.winner == None else g.winner
        points_changed_pl = PointsChanged.objects.all().filter(game=g).filter(player=g.player_left)
        tmp["rp_pl_after"] = points_changed_pl[0].rp_after
        tmp["rp_pl_change"] = points_changed_pl[0].rp_after - points_changed_pl[0].rp_before
        points_changed_pr = PointsChanged.objects.all().filter(game=g).filter(player=g.player_right)
        tmp["rp_pr_after"] = points_changed_pr[0].rp_after
        tmp["rp_pr_change"] = points_changed_pr[0].rp_after - points_changed_pr[0].rp_before
        tmp["subgames"] = g.subgames()
        games.append(tmp)
    return games

def create_tournament_table():
    tournaments_list = Tournament.objects.all().order_by('start_time').reverse()
    tournaments = []
    for t in tournaments_list:
        tmp = {}
        tmp["pk"] = t.pk
        tmp["start_time"] = t.start_time
        tmp["name"] = t.name
        tmp["winner"] = t.winner()
        tmp["players"] = len(t.players.all())
        tmp["games"] = len(t.games())
        tmp["ante"] = t.ante
        tmp["total_ante"] = t.total_ante
        tmp["finished"] = t.finished
        tournaments.append(tmp)
    return tournaments

def tournaments(request):
    context = {
        'tournaments' : create_tournament_table()
    }
    return render(request, 'index/tournaments.html', context)

@login_required
def add_tournament(request):
    tournament_form = TournamentCreateForm()
    tournament_placing_ante_formset = TournamentPlacingAnteFormSet(instance=Tournament())

    context = {
        'tournament_form'                 : tournament_form,
        'tournament_placing_ante_formset' : tournament_placing_ante_formset,
    }
    return render(request, 'index/add_tournament.html', context)

@login_required
def submit_tournament(request):
    tournament_form = TournamentCreateForm(request.POST)

    if tournament_form.is_valid():
        tournament = tournament_form.save(commit=False)
        tournament_placing_ante_formset = TournamentPlacingAnteFormSet(request.POST,
                                                                       instance=tournament)
        # FIXME this is not valid here, since the tournament for each tpa has not
        # been setup yet
        #if not tournament_placing_ante_formset.is_valid():
        #    return redirect('index.views.error')

        tournament.total_ante = 0
        tournament.save()
        tournament_form.save_m2m()

        total_ante = 0
        points_changed_list = []
        players = tournament.players.all()
        for player in players:
            points_changed = PointsChanged(player=player, tournament=tournament,
                                           rp_before=player.ranking_points,
                                           pp_before=player.pool_points)
            calculated_ante = player.calculate_ante_percentage(tournament.ante,
                                                               tournament.pool_points)
            player.ranking_points = calculated_ante["rp"] - calculated_ante["ante"]
            player.pool_points = calculated_ante["pp"]
            # this will be set to a correct value when the tournament
            # is saved
            points_changed.rp_after = calculated_ante["rp"]
            points_changed.pp_after = calculated_ante["pp"]
            total_ante = total_ante + calculated_ante["ante"]
            points_changed_list.append(points_changed)

        total_placing_ante = 0
        for form in tournament_placing_ante_formset.forms:
            tpa = form.save(commit = False)
            total_placing_ante = total_placing_ante + tpa.ante

        if total_ante != total_placing_ante:
            tournament.delete()
            return redirect('index.views.error')

        for player in players:
            player.save()
        for points_changed in points_changed_list:
            points_changed.save()
        tournament.total_ante = total_ante
        tournament.save()
        tournament_form.save_m2m()

        for form in tournament_placing_ante_formset.forms:
            tpa = form.save(commit = False)
            tpa.tournament = tournament
            tpa.save()
            form.save_m2m()

        return redirect('index.views.edit_tournament', tournament.pk)
    else:
        return redirect('index.views.error')

def prepare_tournament_context(tournament_id, form):
    instance = get_object_or_404(Tournament, pk=tournament_id)
    tournament_form = form(instance=instance)
    played_game_form = PlayedGameForm(initial={'tournament' : instance},
                                      available_players=instance.players.all())
    subgame_formset = SubgameFormSet(instance=PlayedGame())

    tpas = TournamentPlacingAnte.objects.all().filter(tournament=instance)
    tournament_placing_ante_formset = TournamentPlacingAnteSubmitFormSet(instance=instance)
    tournament_placing_ante_formset.form = wraps(TournamentPlacingAnteSubmitForm)(partial(TournamentPlacingAnteSubmitForm, available_players=instance.players.all()))
    tournament_extra_data = {}
    tournament_extra_data["tournament_pk"] = tournament_id
    tournament_extra_data["players"] = instance.players.all()
    all_games_in_tournament_by_date = instance.games().order_by('start_time').reverse()
    tournament_extra_data["games"] = create_games_table(all_games_in_tournament_by_date)
    context = {
        'played_game_form'                : played_game_form,
        'subgame_formset'                 : subgame_formset,
        'tournament_form'                 : tournament_form,
        'tournament_placing_ante_formset' : tournament_placing_ante_formset,
        'tournament_extra_data'           : tournament_extra_data,
    }
    return context

@login_required
def edit_tournament(request, tournament_id):
    return render(request, 'index/edit_tournament.html',
                  prepare_tournament_context(tournament_id,
                                             TournamentEditForm))

def view_tournament(request, tournament_id):
    return render(request, 'index/view_tournament.html',
                  prepare_tournament_context(tournament_id,
                                             TournamentEditForm))

@login_required
def save_tournament(request, tournament_id):
    instance = get_object_or_404(Tournament, id=tournament_id)
    tournament_form = TournamentEditForm(request.POST, instance=instance)

    if tournament_form.is_valid():
        tournament = tournament_form.save(commit = False)
        tournament_placing_ante_formset = TournamentPlacingAnteSubmitFormSet(request.POST,
                                               instance=tournament)

        if not tournament_placing_ante_formset.is_valid():
            return redirect('index.views.error')

        tournament.save()
        tournament_form.save_m2m()

        for form in tournament_placing_ante_formset.forms:
            tpa = form.save(commit=False)
            tpa.tournament = tournament
            tpa.save()
            form.save_m2m()

        # tournament finished. Hand out points
        if tournament.finished:
            tournament.distribute_points()

        return redirect('index.views.tournaments')
    else:
        return redirect('index.views.error')

@login_required
def add_game(request):
    played_game_form = PlayedGameForm(available_players=Player.objects.active_players())
    subgame_formset = SubgameFormSet(instance=PlayedGame())

    context = {
        'played_game_form' : played_game_form,
        'subgame_formset'  : subgame_formset,
    }

    return render(request, 'index/add_game.html', context)

@login_required
def submit_game(request, tournament_id=None):
    tournament = None
    if tournament_id != None:
        tournament = get_object_or_404(Tournament, id=tournament_id)
    played_game_form = PlayedGameForm(request.POST)

    if played_game_form.is_valid():
        played_game = played_game_form.save(commit=False)
        played_game.tournament = tournament
        if (tournament != None):
            played_game.ranked = False
        subgame_formset = SubgameFormSet(request.POST, request.FILES, instance=played_game)

        if not subgame_formset.is_valid():
            return redirect('index.views.error')

        pl = played_game.player_left
        pr = played_game.player_right
        winner = played_game.winner
        if (pl == pr or (winner != pl and winner != pr and winner != None)):
            return redirect('index.views.error')

        subgames = []
        for form in subgame_formset.forms:
            subgames.append(form.save(commit=False))

        points_changed_pl = PointsChanged(tournament=tournament, player=pl,
                                          rp_before=pl.ranking_points,
                                          pp_before=pl.pool_points)
        points_changed_pr = PointsChanged(tournament=tournament, player=pr,
                                          rp_before=pr.ranking_points,
                                          pp_before=pr.pool_points)

        if played_game.ranked:
            if winner == None:
                # if there is no winner, each player gets half of the ante
                # if this is not an even sum, give the remainder to the player
                # who had the most lives left in the match. If both are equal,
                # give it to the player with the fewest ranking points. If both
                # are still equal, give it to the left player
                pl_ante = pl.calculate_ranked_ante()
                pr_ante = pr.calculate_ranked_ante()
                pl.pool_points = pl_ante["pp"]
                pr.pool_points = pr_ante["pp"]

                ante = (pl_ante["ante"] + pr_ante["ante"]) / 2
                ante_rem = (pl_ante["ante"] + pr_ante["ante"]) % 2
                pl.ranking_points = pl_ante["rp"] - pl_ante["ante"] + ante
                pr.ranking_points = pr_ante["rp"] - pr_ante["ante"] + ante
                if ante_rem != 0:
                    pl_lives = 0
                    pr_lives = 0
                    for subgame in subgames:
                        pl_lives = pl_lives + subgame.pl_lives
                        pr_lives = pr_lives + subgame.pr_lives
                    if pl_lives == pr_lives:
                        if pl.ranking_points >= pr.ranking_points:
                            pl.ranking_points = pl.ranking_points + 1
                        else:
                            pr.ranking_points = pr.ranking_points + 1
                    elif pl_lives > pr_lives:
                        pl.ranking_points = pl.ranking_points + 1
                    else:
                        pr.ranking_points = pr.ranking_points + 1
            else:
                # if there is a winner, this calculation is used
                loser = pl if winner == pr else pr
                # the line below is needed due to winner and (pl|pr) not actually
                # pointing to the same thing somehow, which messes up ranking points
                # and pool points
                winner = pl if winner == pl else pr

                winner_ante = winner.calculate_ranked_ante()
                loser_ante = loser.calculate_ranked_ante()
                winner.pool_points = winner_ante["pp"]
                loser.pool_points = loser_ante["pp"]

                winner.ranking_points = winner_ante["rp"] + loser_ante["ante"]
                loser.ranking_points = loser_ante["rp"] - loser_ante["ante"]

        points_changed_pl.pp_after = pl.pool_points
        points_changed_pl.rp_after = pl.ranking_points
        points_changed_pr.pp_after = pr.pool_points
        points_changed_pr.rp_after = pr.ranking_points

        pl.save()
        pr.save()
        played_game.save()
        played_game_form.save_m2m()

        points_changed_pl.game = played_game
        points_changed_pr.game = played_game
        points_changed_pl.save()
        points_changed_pr.save()

        for subgame in subgames:
            subgame.parent = played_game
            subgame.save()
        for form in subgame_formset.forms:
            form.save_m2m()

        if request.is_ajax():
            return HttpResponse()
        else:
            return redirect('index.views.ranking')
    else:
        return redirect('index.views.error')

@login_required
def update_total_ante(request):
    if request.is_ajax():
        try:
            players_id = request.POST.getlist( 'players')
            players = Player.objects.all().filter(pk__in=players_id)
            ante_percentage = int(request.POST['ante'])
            pool_points = int(request.POST['pool_points'])
            total_ante = 0
            for player in players:
                total_ante = total_ante + player.calculate_ante_percentage(ante_percentage,
                                                                           pool_points)["ante"]
            return HttpResponse(str(total_ante))
        except ValueError:
            return HttpResponse('Error') # incorrect post
    else:
        raise Http404

def get_games_list(request, tournament_id):
    if request.is_ajax():
        tournament = get_object_or_404(Tournament, id=tournament_id)
        all_games_in_tournament_by_date = tournament.games().order_by('start_time').reverse()
        context = {
            'games' : create_games_table(all_games_in_tournament_by_date)
        }
        return render(request, 'index/includes/list_games.html', context)
    else:
        raise Http404

def get_players_list(request):
    if request.is_ajax():
        str_body = request.body.decode('utf-8')
        data = json.loads(str_body)
        all_time = data['all_time']
        active_only = data['active_only']
        print(all_time)
        if all_time == "True":
            print("all time")
            player_table = create_player_table(active_only, since=datetime.date(1970, 1, 1))
        else:
            player_table = create_player_table(active_only)
        context = {
            'players' : player_table,
        }
        return render(request, 'index/includes/list_players.html', context)
    else:
        raise Http404

def error(request):
    return render(request, 'index/error.html')

def internal_info(request):
    total_ranking_points = sum(map(lambda p: p.total_points(), Player.objects.all()))
    num_players = len(Player.objects.all())
    rp_per_player = total_ranking_points / num_players
    context = {
        'num_players' : num_players,
        'total_ranking_points' : total_ranking_points,
        'rp_per_player' : rp_per_player,
    }
    return render(request, 'index/internal_info.html', context)

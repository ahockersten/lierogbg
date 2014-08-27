##
# @module index
# @file views.py
#

from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template import Context
from django.contrib.auth.decorators import login_required
from index.models import Player, PlayedGameForm, PlayedGame, Subgame, SubgameForm, SubgameFormSet

def ranking(request):
    context = Context({
        'players' : create_player_table()
    })

    return render(request, 'index/ranking.html', context)

def create_player_table():
    player_list = Player.objects.all().order_by('ranking_points').reverse()
    players = []
    current_rank = 1
    for p in player_list:
        tmp = {}
        tmp["current_rank"] = current_rank
        tmp["name"] = p.name
        tmp["ranking_points"] = p.ranking_points
        tmp["pool_points"] = p.pool_points
        tmp["games"] = len(PlayedGame.objects.all().filter(Q(player_left=p) |
                                                           Q(player_right=p)))
        tmp["wins"] = len(PlayedGame.objects.all().filter(winner=p))
        tmp["losses"] = tmp["games"] - tmp["wins"]
        players.append(tmp)
        current_rank = current_rank + 1
    return players

def games(request):
    context = Context({
        'games' : create_games_table()
    })

    return render(request, 'index/games.html', context)

def create_games_table():
    games_list = PlayedGame.objects.all().order_by('start_time').reverse()
    games = []
    for g in games_list:
        tmp = {}
        tmp["start_time"] = g.start_time
        tmp["player_left"] = g.player_left
        tmp["player_right"] = g.player_right
        tmp["winner"] = g.winner
        tmp["rp_pl"] = g.rp_pl_after
        tmp["rp_pl_change"] = g.rp_pl_after - g.rp_pl_before
        tmp["rp_pl_positive"] = True if g.rp_pl_after - g.rp_pl_before >= 0 else False
        tmp["rp_pr"] = g.rp_pr_after
        tmp["rp_pr_change"] = g.rp_pr_after - g.rp_pr_before
        tmp["rp_pr_positive"] = True if g.rp_pr_after - g.rp_pr_before >= 0 else False
        games.append(tmp)
    return games

@login_required
def add_game(request):
    played_game_form = PlayedGameForm()
    subgame_formset = SubgameFormSet(instance=PlayedGame())

    context = Context({
        'played_game_form' : played_game_form,
        'subgame_formset'  : subgame_formset,
    })

    return render(request, 'index/add_game.html', context)

@login_required
def submit_game(request):
    played_game_form = PlayedGameForm(request.POST)

    if played_game_form.is_valid():
        played_game = played_game_form.save(commit=False)
        subgame_formset = SubgameFormSet(request.POST, instance=played_game)

        if not subgame_formset.is_valid():
            return redirect('index.views.error')

        pl = played_game.player_left
        pr = played_game.player_right
        winner = played_game.winner
        if (pl == pr or (winner != pl and winner != pr)):
            return redirect('index.views.error')
        loser = pl if winner == pr else pr
        # the line below is needed due to winner and (pl|pr) not actually
        # pointing to the same thing somehow, which messes up ranking points
        # and pool points
        winner = pl if winner == pl else pr

        played_game.rp_pl_before = pl.ranking_points
        played_game.rp_pr_before = pr.ranking_points
        played_game.pp_pl_before = pl.pool_points
        played_game.pp_pr_before = pr.pool_points

        ante_multiplier = 0.02
        if (winner.pool_points != 0):
            winner.ranking_points = winner.ranking_points + min(winner.pool_points, 40)
            winner.pool_points = winner.pool_points - min(winner.pool_points, 40)
        if (loser.pool_points != 0):
            loser.ranking_points = loser.ranking_points + min(loser.pool_points, 40)
            loser.pool_points = loser.pool_points - min(loser.pool_points, 40)
        loser_ante = round(((loser.ranking_points) ** 2) * 0.001 * ante_multiplier)
        if loser_ante == 0:
            loser_ante = 1
        winner.ranking_points = winner.ranking_points + loser_ante
        loser.ranking_points = loser.ranking_points - loser_ante

        played_game.rp_pl_after = pl.ranking_points
        played_game.rp_pr_after = pr.ranking_points
        played_game.pp_pl_after = pl.pool_points
        played_game.pp_pr_after = pr.pool_points

        winner.save()
        loser.save()
        played_game.save()
        played_game_form.save_m2m()

        for form in subgame_formset.forms:
            subgame = form.save(commit=False)
            subgame.parent = played_game
            subgame.save()
            form.save_m2m()

        return redirect('index.views.ranking')
    else:
        return redirect('index.views.error')

def error(request):
    context = Context({})
    return render(request, 'index/error.html', context)

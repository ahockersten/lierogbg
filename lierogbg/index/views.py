##
# @module index
# @file views.py
#

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template import Context
from django.contrib.auth.decorators import login_required
from index.models import Player, PlayedGameForm

def index(request):
    context = Context({
        'players' : create_player_table()
    })

    return render(request, 'index/index.html', context)

def create_player_table():
    player_list = Player.objects.all().order_by('ranking_points').reverse()
    players = []
    current_rank = 1
    for p in player_list:
        players.append((current_rank, p.name, p.ranking_points, p.pool_points))
        current_rank = current_rank + 1
    return players

@login_required
def add_game(request):
    played_game_form = PlayedGameForm()

    context = Context({
        'played_game_form' : played_game_form
    })

    return render(request, 'index/add_game.html', context)

@login_required
def submit_game(request):
    played_game_form = PlayedGameForm(request.POST)
    if played_game_form.is_valid():
        pl = played_game_form.cleaned_data['player_left']
        pr = played_game_form.cleaned_data['player_right']
        winner = played_game_form.cleaned_data['winner']
        if (pl == pr or (winner != pl and winner != pr)):
            return redirect('index.views.error')
        loser = pl if winner == pr else pr
        ante_multiplier = 0.02
        if (winner.pool_points != 0):
            winner.ranking_points = winner.ranking_points + min(winner.pool_points, 40)
            winner.pool_points = winner.pool_points - min(winner.pool_points, 40)
        if (loser.pool_points != 0):
            loser.ranking_points = loser.ranking_points + min(loser.pool_points, 40)
            loser.pool_points = loser.pool_points - min(loser.pool_points, 40)
        loser_ante = round(((loser.ranking_points + loser.pool_points) ** 2) * 0.001 * ante_multiplier)
        if loser_ante == 0:
            loser_ante = 1
        winner.ranking_points = winner.ranking_points + loser_ante
        loser.ranking_points = loser.ranking_points - loser_ante
        winner.save()
        loser.save()
        return redirect('index.views.index')
    else:
        return redirect('index.views.error')

def error(request):
    context = Context({})
    return render(request, 'index/error.html', context)

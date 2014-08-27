##
# @module index
# @file views.py
#

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template import Context
from django.contrib.auth.decorators import login_required
from index.models import Player

@login_required
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

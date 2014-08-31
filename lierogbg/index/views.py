##
# @module index
# @file views.py
#

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.utils.translation import ugettext_lazy as _
from index.models import Player, PlayedGameForm, PlayedGame, Subgame, SubgameForm
from index.models import SubgameFormSet, Tournament, TournamentPlacingAnte
from index.models import TournamentPlacingAnteSubmitFormSet, TournamentPlacingAnteFormSet
from index.models import TournamentCreateForm, TournamentEditForm

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
        tmp["player"] = p
        tmp["current_rank"] = current_rank
        games = PlayedGame.objects.all().filter(Q(player_left=p) |
                                                Q(player_right=p))
        tmp["games"] = len(games)
        tmp["wins"] = len(games.filter(winner=p))
        tmp["ties"] = len(games.filter(winner=None))
        tmp["losses"] = tmp["games"] - tmp["wins"] - tmp["ties"]
        lives = 0
        for g in games:
            subgames = Subgame.objects.all().filter(parent=g)
            for s in subgames:
                if g.player_left == p:
                    lives = lives + s.pl_lives
                    lives = lives - s.pr_lives
                else:
                    lives = lives - s.pl_lives
                    lives = lives + s.pr_lives
        tmp["lives"] = lives
        tmp["lives_positive"] = True if lives >= 0 else False
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
        tmp["game"] = g
        tmp["winner"] = _('Tied') if g.winner == None else g.winner
        tmp["rp_pl_change"] = g.rp_pl_after - g.rp_pl_before
        tmp["rp_pl_positive"] = True if g.rp_pl_after - g.rp_pl_before >= 0 else False
        tmp["rp_pr_change"] = g.rp_pr_after - g.rp_pr_before
        tmp["rp_pr_positive"] = True if g.rp_pr_after - g.rp_pr_before >= 0 else False
        subgames = Subgame.objects.all().filter(parent=g)
        subgames_tmp = []
        for subgame in subgames:
            subgames_tmp.append((subgame.map_played, subgame.pl_lives,
                                 subgame.pr_lives, subgame.replay_file))
        tmp["subgames"] = subgames_tmp
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
        print TournamentPlacingAnte.objects.all()
        print TournamentPlacingAnte.objects.all().filter(tournament=t)
        print TournamentPlacingAnte.objects.all().filter(tournament=t).filter(placing=1)
        tmp["winner"] = TournamentPlacingAnte.objects.all().filter(tournament=t).filter(placing=1)[0].player
        tmp["players"] = len(t.players.all())
        tmp["games"] = len(PlayedGame.objects.all().filter(tournament=t))
        tmp["ante"] = t.ante
        tmp["total_ante"] = t.total_ante
        tmp["finished"] = t.finished
        tournaments.append(tmp)
    return tournaments

def tournaments(request):
    context = Context({
        'tournaments' : create_tournament_table()
    })
    return render(request, 'index/tournaments.html', context)

@login_required
def add_tournament(request):
    tournament_form = TournamentCreateForm()
    tournament_placing_ante_formset = TournamentPlacingAnteFormSet(instance=Tournament())

    context = Context({
        'tournament_form'                 : tournament_form,
        'tournament_placing_ante_formset' : tournament_placing_ante_formset,
    })
    return render(request, 'index/add_tournament.html', context)

@login_required
def edit_tournament(request, tournament):
    instance = get_object_or_404(Tournament, pk=tournament)
    tournament_form = TournamentEditForm(instance=instance)

    tpas = TournamentPlacingAnte.objects.all().filter(tournament=instance)
    tournament_placing_ante_formset = TournamentPlacingAnteSubmitFormSet(instance=instance)
    tournament_extra_data = {}
    tournament_extra_data["players"] = instance.players.all()
    context = Context({
        'tournament_form' : tournament_form,
        'tournament_placing_ante_formset' : tournament_placing_ante_formset,
        'tournament_extra_data' : tournament_extra_data,
    })
    return render(request, 'index/edit_tournament.html', context)

@login_required
def submit_tournament(request):
    tournament_form = TournamentCreateForm(request.POST)

    if tournament_form.is_valid():
        tournament = tournament_form.save(commit = False)
        tournament_placing_ante_formset = TournamentPlacingAnteFormSet(request.POST,
                                                                       instance=tournament)

        # FIXME this is not valid here, since the tournament for each has not
        # been setup yet
        #if not tournament_placing_ante_formset.is_valid():
        #    return redirect('index.views.error')

        # FIXME need to validate that the total_ante calculated
        # is the same as the sum of all placings' antes. The
        # javascript should ensure that this is always true,
        # but I don't trust it
        tournament.total_ante = 0
        tournament.save()
        tournament_form.save_m2m()
        total_ante = 0
        print "a"
        for player in tournament.players.all():
            # FIXME this should be reused for update_total_ante
            if (player.pool_points != 0):
                player.ranking_points = player.ranking_points + min(player.pool_points, tournament.pool_points)
            player_ante = int(round(player.ranking_points * tournament.ante * 0.01))
            if player_ante == 0 and player.ranking_points != 0:
                player_ante = 1
            player.ranking_points = player.ranking_points - player_ante
            player.save()
            total_ante = total_ante + player_ante
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
        subgame_formset = SubgameFormSet(request.POST, request.FILES, instance=played_game)

        if not subgame_formset.is_valid():
            return redirect('index.views.error')

        pl = played_game.player_left
        pr = played_game.player_right
        winner = played_game.winner
        if (pl == pr or (winner != pl and winner != pr and winner != None)):
            return redirect('index.views.error')

        played_game.rp_pl_before = pl.ranking_points
        played_game.rp_pr_before = pr.ranking_points
        played_game.pp_pl_before = pl.pool_points
        played_game.pp_pr_before = pr.pool_points

        ante_multiplier = 0.02
        if (pl.pool_points != 0):
            pl.ranking_points = pl.ranking_points + min(pl.pool_points, 40)
            pl.pool_points = pl.pool_points - min(pl.pool_points, 40)
        if (pr.pool_points != 0):
            pr.ranking_points = pr.ranking_points + min(pr.pool_points, 40)
            pr.pool_points = pr.pool_points - min(pr.pool_points, 40)

        subgames = []
        for form in subgame_formset.forms:
            subgames.append(form.save(commit=False))

        if winner == None:
            # if there is no winner, each player gets half of the ante
            # if this is not an even sum, give the remainder to the player
            # who had the most lives left in the match. If both are equal,
            # give it to the player with the fewest ranking points. If both
            # are still equal, give it to the left player
            pl_ante = round(((pl.ranking_points) ** 2) * 0.001 * ante_multiplier)
            pr_ante = round(((pr.ranking_points) ** 2) * 0.001 * ante_multiplier)
            ante = (pl_ante + pr_ante) / 2
            ante_rem = (pl_ante + pr_ante) % 2
            pl.ranking_points = pl.ranking_points - pl_ante + ante
            pr.ranking_points = pr.ranking_points - pr_ante + ante
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
            loser = pl if winner == pr else pr
            # the line below is needed due to winner and (pl|pr) not actually
            # pointing to the same thing somehow, which messes up ranking points
            # and pool points
            winner = pl if winner == pl else pr

            loser_ante = round(((loser.ranking_points) ** 2) * 0.001 * ante_multiplier)
            if loser_ante == 0 and loser.ranking_points != 0:
                loser_ante = 1
            winner.ranking_points = winner.ranking_points + loser_ante
            loser.ranking_points = loser.ranking_points - loser_ante

        played_game.rp_pl_after = pl.ranking_points
        played_game.rp_pr_after = pr.ranking_points
        played_game.pp_pl_after = pl.pool_points
        played_game.pp_pr_after = pr.pool_points

        pl.save()
        pr.save()
        played_game.save()
        played_game_form.save_m2m()

        for subgame in subgames:
            subgame.parent = played_game
            subgame.save()
        for form in subgame_formset.forms:
            form.save_m2m()

        return redirect('index.views.ranking')
    else:
        return redirect('index.views.error')

@login_required
def update_total_ante(request):
    if request.is_ajax():
        try:
            players_id = request.POST.getlist( 'players')
            players = Player.objects.all().filter(pk__in = players_id)
            ante = int(request.POST['ante']) * 0.01
            pool_points = int(request.POST['pool_points'])
            total_ante = 0
            for player in players:
                if (player.pool_points != 0):
                    player.ranking_points = player.ranking_points + min(player.pool_points, pool_points)
                player_ante = round(player.ranking_points * ante)
                if player_ante == 0 and player.ranking_points != 0:
                    player_ante = 1
                total_ante = total_ante + player_ante
            return HttpResponse(str(total_ante))
        except ValueError:
            return HttpResponse('Error') # incorrect post
    else:
        raise Http404

def error(request):
    context = Context({})
    return render(request, 'index/error.html', context)

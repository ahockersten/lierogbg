"""
Views for the ranking module
"""

import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _
from functools import partial, wraps
from rankings.forms import PlayedGameForm, SubgameFormSet
from rankings.forms import TournamentCreateForm, TournamentEditForm
from rankings.forms import TournamentPlacingAnteFormSet
from rankings.forms import TournamentPlacingAnteSubmitForm
from rankings.forms import TournamentPlacingAnteSubmitFormSet
from rankings.models import PlayedGame
from rankings.models import Player
from rankings.models import PointsChanged
from rankings.models import Tournament

# Number of games to display per page in the game list
GAME_PAGE_LIMIT = 30


def ranking(request, active_only):
    """
    Displays the current ranking
    """
    last_game_time = None
    last_game = PlayedGame.objects.last_game()
    if last_game is not None:
        last_game_time = last_game.start_time.isoformat()
    context = {
        'players': create_player_table(active_only),
        'last_game_time': last_game_time,
    }

    return render(request, 'rankings/ranking.html', context)


def create_player_table(active_only,
                        since=datetime.datetime(
                            datetime.datetime.today().year, 1, 1)):
    """
    Creates the table of all players and their rankings.
    If active_only is set to True, it only displays active players.
    Only data since 'since' is displayed.
    """
    shown_players = None
    if active_only == 'True':
        shown_players = Player.objects.active_players()
    else:
        shown_players = Player.objects.all()
    player_list = sorted(shown_players, key=lambda p: p.ranking_points,
                         reverse=True) if shown_players else []
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
    """
    Display data about the latest GAME_PAGE_LIMIT number of games.
    """
    all_pg = PlayedGame.objects.all().order_by('start_time')
    first_games_by_date = all_pg.reverse()[:GAME_PAGE_LIMIT]
    last_game = PlayedGame.objects.last_game()
    last_game_time = None
    if last_game is not None:
        last_game_time = last_game.start_time.isoformat()
    context = {
        'games': create_games_table(first_games_by_date),
        'current_match': 0,
        'next_match': GAME_PAGE_LIMIT,
        'last_game_time': last_game_time,
        'show_all': False,
    }
    return render(request, 'rankings/games.html', context)


def create_games_table(games_list):
    """
    Creates a table with information about all games in games_list
    """
    ret = []
    for g in games_list:
        tmp = {}
        tmp["game"] = g
        tmp["winner"] = _('Tied') if g.winner is None else g.winner
        all_pc = PointsChanged.objects.all()
        pc_pl = all_pc.filter(game=g).filter(player=g.player_left)
        if pc_pl.exists():
            tmp["rp_pl_after"] = pc_pl[0].rp_after
            tmp["rp_pl_change"] = pc_pl[0].rp_after - pc_pl[0].rp_before
        pc_pr = all_pc.filter(game=g).filter(player=g.player_right)
        if pc_pl.exists():
            tmp["rp_pr_after"] = pc_pr[0].rp_after
            tmp["rp_pr_change"] = pc_pr[0].rp_after - pc_pr[0].rp_before
        tmp["subgames"] = g.subgames()
        ret.append(tmp)
    return ret


def create_tournament_table():
    """
    Creates a table wiith information about all tournaments.
    """
    all_tournaments = Tournament.objects.all()
    tournaments_list = all_tournaments.order_by('start_time').reverse()
    ret = []
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
        ret.append(tmp)
    return ret


def tournaments(request):
    """
    Renders a list of all tournaments.
    """
    context = {
        'tournaments': create_tournament_table()
    }
    return render(request, 'rankings/tournaments.html', context)


@login_required
def add_tournament(request):
    """
    Renders the page used for adding a new tournament
    """
    tournament_form = TournamentCreateForm()
    tournament_placing_ante_formset = TournamentPlacingAnteFormSet(
        instance=Tournament())
    context = {
        'tournament_form': tournament_form,
        'tournament_placing_ante_formset': tournament_placing_ante_formset,
    }
    return render(request, 'rankings/add_tournament.html', context)


@login_required
def submit_tournament(request):
    """
    Submit a new tournament.
    """
    tournament_form = TournamentCreateForm(request.POST)

    if tournament_form.is_valid():
        tournament = tournament_form.save(commit=False)
        tournament_placing_ante_formset = TournamentPlacingAnteFormSet(
            request.POST, instance=tournament)
        # FIXME this is not valid here, since the tournament for each tpa has
        # not been setup yet
        # if not tournament_placing_ante_formset.is_valid():
        #    return redirect('rankings.views.error')

        tournament.total_ante = 0
        tournament.save()
        tournament_form.save_m2m()

        total_ante = 0
        points_changed_list = []
        players = tournament.players.all()
        for p in players:
            points_changed = PointsChanged(player=p,
                                           tournament=tournament,
                                           rp_before=p.ranking_points,
                                           pp_before=p.pool_points)
            calculated_ante = p.calculate_ante_percentage(
                tournament.ante, tournament.pool_points)
            # this will be set to a correct value when the tournament
            # is saved
            points_changed.rp_after = calculated_ante["rp"] - \
                calculated_ante["ante"]
            points_changed.pp_after = calculated_ante["pp"]
            total_ante = total_ante + calculated_ante["ante"]
            points_changed_list.append(points_changed)

        total_placing_ante = 0
        for form in tournament_placing_ante_formset.forms:
            tpa = form.save(commit=False)
            total_placing_ante = total_placing_ante + tpa.ante

        if total_ante != total_placing_ante:
            tournament.delete()
            return redirect('rankings.views.error')

        for p in players:
            p.save()
        for points_changed in points_changed_list:
            points_changed.save()
        tournament.total_ante = total_ante
        tournament.save()
        tournament_form.save_m2m()

        for form in tournament_placing_ante_formset.forms:
            tpa = form.save(commit=False)
            tpa.tournament = tournament
            tpa.save()
            form.save_m2m()

        return redirect('rankings.views.edit_tournament', tournament.pk)
    else:
        return redirect('rankings.views.error')


def prepare_tournament_context(tournament_id, form):
    """
    Prepares the context for a tournament.
    """
    instance = Tournament.objects.get(pk=tournament_id)
    tournament_form = form(instance=instance)
    played_game_form = PlayedGameForm(
        initial={'tournament': instance},
        available_players=instance.players.all())
    subgame_formset = SubgameFormSet(instance=PlayedGame())

    tournament_placing_ante_formset = TournamentPlacingAnteSubmitFormSet(
        instance=instance)
    tournament_placing_ante_formset.form = wraps(
        TournamentPlacingAnteSubmitForm)(partial(
            TournamentPlacingAnteSubmitForm,
            available_players=instance.players.all()))
    tournament_extra_data = {}
    tournament_extra_data["tournament_pk"] = tournament_id
    tournament_extra_data["players"] = instance.players.all()
    games_in_tournament = instance.games().order_by('start_time').reverse()
    tournament_extra_data["games"] = create_games_table(games_in_tournament)
    context = {
        'played_game_form': played_game_form,
        'subgame_formset': subgame_formset,
        'tournament_form': tournament_form,
        'tournament_placing_ante_formset': tournament_placing_ante_formset,
        'tournament_extra_data': tournament_extra_data,
    }
    return context


@login_required
def edit_tournament(request, tournament_id):
    """
    Renders the edit page for a tournament.
    """
    try:
        context = prepare_tournament_context(tournament_id,
                                             TournamentEditForm)
        return render(request, 'rankings/edit_tournament.html', context)
    except ValueError:
        return redirect('rankings.views.error')


def view_tournament(request, tournament_id):
    """
    Renders the viewing page for a tournament.
    """
    try:
        context = prepare_tournament_context(tournament_id,
                                             TournamentEditForm)
        return render(request, 'rankings/view_tournament.html', context)
    except ValueError:
        return redirect('rankings.views.error')


@login_required
def save_tournament(request, tournament_id):
    """
    Save a tournament.
    """
    instance = get_object_or_404(Tournament, id=tournament_id)
    tournament_form = TournamentEditForm(request.POST, instance=instance)

    if tournament_form.is_valid():
        tournament = tournament_form.save(commit=False)
        tournament_placing_ante_formset = TournamentPlacingAnteSubmitFormSet(
            request.POST, instance=tournament)

        if not tournament_placing_ante_formset.is_valid():
            return redirect('rankings.views.error')

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

        return redirect('rankings.views.tournaments')
    else:
        return redirect('rankings.views.error')


@login_required
def add_game(request):
    """
    Renders the "add game" page.
    """
    played_game_form = PlayedGameForm(
        available_players=Player.objects.active_players())
    subgame_formset = SubgameFormSet(instance=PlayedGame())

    context = {
        'played_game_form': played_game_form,
        'subgame_formset': subgame_formset,
    }

    return render(request, 'rankings/add_game.html', context)


@login_required
def submit_game(request, tournament_id=None):
    """
    Submit a game. Will calculate new rp/pp etc if this is a ranked game.
    FIXME split this up somehow
    """
    tournament = None
    if tournament_id is not None:
        tournament = get_object_or_404(Tournament, id=tournament_id)
    played_game_form = PlayedGameForm(request.POST)

    if played_game_form.is_valid():
        played_game = played_game_form.save(commit=False)
        played_game.tournament = tournament
        if tournament is not None:
            played_game.ranked = False
            # can't add games to finished tournaments
            if tournament.finished:
                return redirect('rankings.views.error')
        subgame_formset = SubgameFormSet(request.POST, request.FILES,
                                         instance=played_game)

        if not subgame_formset.is_valid():
            return redirect('rankings.views.error')

        pl = played_game.player_left
        pr = played_game.player_right
        winner = played_game.winner
        if pl == pr or (winner != pl and winner != pr and winner is not None):
            return redirect('rankings.views.error')

        subgames = []
        for form in subgame_formset.forms:
            subgames.append(form.save(commit=False))

        pc_pl = PointsChanged(tournament=tournament, player=pl,
                              rp_before=pl.ranking_points,
                              pp_before=pl.pool_points)
        pc_pr = PointsChanged(tournament=tournament, player=pr,
                              rp_before=pr.ranking_points,
                              pp_before=pr.pool_points)

        if played_game.ranked:
            if winner is None:
                # if there is no winner, each player gets half of the ante
                # if this is not an even sum, give the remainder to the player
                # who had the most lives left in the match. If both are equal,
                # give it to the player with the fewest ranking points. If both
                # are still equal, give it to the left player
                pl_ante = pl.calculate_ranked_ante()
                pr_ante = pr.calculate_ranked_ante()
                pc_pl.pp_after = pl_ante["pp"]
                pc_pr.pp_after = pr_ante["pp"]
                print(pl_ante)
                print(pr_ante)
                ante = (pl_ante["ante"] + pr_ante["ante"]) / 2
                ante_rem = (pl_ante["ante"] + pr_ante["ante"]) % 2
                pc_pl.rp_after = pl_ante["rp"] - pl_ante["ante"] + ante
                pc_pr.rp_after = pr_ante["rp"] - pr_ante["ante"] + ante
                print(pc_pl)
                print(pc_pr)
                if ante_rem != 0:
                    pl_lives = 0
                    pr_lives = 0
                    for subgame in subgames:
                        pl_lives = pl_lives + subgame.pl_lives
                        pr_lives = pr_lives + subgame.pr_lives
                    if pl_lives == pr_lives:
                        if pc_pl.rp_after >= pc_pr.rp_after:
                            pc_pl.rp_after = pc_pl.rp_after + 1
                        else:
                            pc_pr.rp_after = pc_pr.rp_after + 1
                    elif pl_lives > pr_lives:
                        pc_pl.rp_after = pc_pl.rp_after
                    else:
                        pc_pr.rp_after = pc_pr.rp_after + 1
            else:
                # if there is a winner, this calculation is used
                loser = pl if winner == pr else pr
                pc_loser = pc_pl if winner == pr else pc_pr
                # the line below is needed due to winner and (pl|pr) not
                # actually pointing to the same thing somehow, which messes
                # up ranking points and pool points
                winner = pl if winner == pl else pr
                pc_winner = pc_pl if winner == pl else pc_pr

                winner_ante = winner.calculate_ranked_ante()
                loser_ante = loser.calculate_ranked_ante()
                pc_winner.pp_after = winner_ante["pp"]
                pc_loser.pp_after = loser_ante["pp"]

                pc_winner.rp_after = winner_ante["rp"] + loser_ante["ante"]
                pc_loser.rp_after = loser_ante["rp"] - loser_ante["ante"]
        else:
            pc_pl.pp_after = pl.pool_points
            pc_pl.rp_after = pl.ranking_points
            pc_pr.pp_after = pr.pool_points
            pc_pr.rp_after = pr.ranking_points

        pl.save()
        pr.save()
        played_game.save()
        played_game_form.save_m2m()

        pc_pl.game = played_game
        pc_pr.game = played_game
        pc_pl.save()
        pc_pr.save()
        print(pc_pl)
        print(pc_pr)

        for subgame in subgames:
            subgame.parent = played_game
            subgame.save()
        for form in subgame_formset.forms:
            form.save_m2m()

        if request.is_ajax():
            return HttpResponse()
        else:
            return redirect('rankings.views.ranking')
    else:
        return redirect('rankings.views.error')


@login_required
def update_total_ante(request):
    """
    Updates the total ante used by all players in the given list.
    """
    if request.is_ajax():
        try:
            players_id = request.POST.getlist('players')
            players = Player.objects.all().filter(pk__in=players_id)
            ante_percentage = int(request.POST['ante'])
            pool_points = int(request.POST['pool_points'])
            total_ante = 0
            for player in players:
                total_ante = total_ante + player.calculate_ante_percentage(
                    ante_percentage, pool_points)["ante"]
            return HttpResponse(str(total_ante))
        except ValueError:
            return HttpResponse('Error')
    else:
        raise Http404


def get_tournament_games_list(request, tournament_id):
    """
    Renders a list of for the tournament view.
    """
    if request.is_ajax():
        context = {}
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            tgames = tournament.games().order_by('start_time').reverse()
            context['games'] = create_games_table(tgames)
            return render(request, 'rankings/includes/list_games.html',
                          context)
        # pylint: disable=no-member
        except Tournament.DoesNotExist:
            return HttpResponse('Error, incorrect parameters')
    else:
        raise Http404


def get_games_list(request):
    """
    Renders a list of games.
    :param request.GET['games']: the (newest - x) games to load.
                                 Defaults to 0.
    :param request.GET['show_all']: Whether or not to show full information
                                    about all games.
    """
    if request.is_ajax():
        context = {}
        games_to_load = 0
        try:
            games_to_load = int(request.GET['games'])
        except MultiValueDictKeyError:
            pass
        context['show_all'] = request.GET['show_all']
        all_games = PlayedGame.objects.all()
        games_by_date = []
        next_match = games_to_load + GAME_PAGE_LIMIT
        games_by_date = all_games.order_by('start_time'). \
            reverse()[games_to_load:next_match]
        context['games'] = create_games_table(games_by_date)
        context['current_match'] = games_to_load
        if next_match < len(all_games):
            context['next_match'] = next_match
        prev_match = games_to_load - GAME_PAGE_LIMIT
        if prev_match > -1:
            context['prev_match'] = prev_match
        if context['show_all'] == "True":
            return render(request, 'rankings/includes/list_games.html',
                          context)
        else:
            return render(request, 'rankings/includes/list_games_hidden.html',
                          context)
    else:
        raise Http404


def get_players_list(request):
    """
    Renders the list of players
    """
    if request.is_ajax():
        all_time = request.GET['all_time']
        active_only = request.GET['active_only']
        if all_time == "True":
            player_table = create_player_table(active_only,
                                               since=datetime.date(1970,
                                                                   1, 1))
        else:
            player_table = create_player_table(active_only)
        context = {
            'players': player_table,
        }
        return render(request, 'rankings/includes/list_players.html', context)
    else:
        raise Http404


def error(request):
    """
    Renders a very generic error page
    """
    return render(request, 'rankings/error.html')


def internal_info(request):
    """
    Displays internal bookkeeping info. No sensitive info, just unnecessary.
    """
    total_ranking_points = sum([p.total_points()
                                for p in Player.objects.all()])
    num_players = len(Player.objects.all())
    rp_per_player = total_ranking_points / num_players
    validations = []
    for p in Player.objects.all():
        validations.append({'name': p.name,
                            'validation': p.validate()})
    context = {
        'num_players': num_players,
        'total_ranking_points': total_ranking_points,
        'rp_per_player': rp_per_player,
        'validations': validations,
    }
    return render(request, 'rankings/internal_info.html', context)

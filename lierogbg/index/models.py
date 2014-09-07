from datetimewidget.widgets import DateTimeWidget
from django.db import models
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from index import fields

class PlayerManager(models.Manager):
    def active_players(self):
        return Player.objects.all().filter(active=True)

# Describes a player. This is separate from the authentication
# system
class Player(models.Model):
    # displayed name
    name = models.CharField(max_length = 100)
    # color used for the worm in the game
    color = fields.ColorField()
    # real name, optional
    real_name = models.CharField(max_length = 100, blank = True)
    # current ranking points
    ranking_points = models.IntegerField(default = 1000)
    # current pool points
    pool_points = models.IntegerField(default = 0)
    # if the player is not active, it is not visible in the ranking table etc
    active = models.BooleanField(default = True)
    # a written comment for this player
    comment = models.CharField(blank = True, max_length = 100000)

    objects = PlayerManager()

    # calculates the ante for a ranked match for this player
    # returns a dictionary consisting of the ante, the new rp and
    # the new pp
    def calculate_ranked_ante(self):
        ante_multiplier = 0.02
        rp = self.ranking_points
        pp = self.pool_points
        if pp != 0:
            rp = rp + min(pp, 40)
            pp = pp - min(pp, 40)
        ante = round(((rp) ** 2) * 0.001 * ante_multiplier)
        if ante == 0 and rp != 0:
            ante = 1
        tmp = {}
        tmp["ante"] = int(ante)
        tmp["rp"] = rp
        tmp["pp"] = pp
        return tmp

    def __unicode__(self):
        return u'%s' % (self.name)

    def clean(self):
        pass

    class Meta:
        ordering = ['name']
        pass

# Describes a tournament. When initially created, it takes the ante from and
# adds pool points to all players. When it is recorded as finished, "finished"
# is set to True and it hands out the ante to the winners.
class Tournament(models.Model):
    # when True, this tournament has ended and points from it have been recorded
    finished = models.BooleanField(default = False)
    # time and date when the tournament started
    start_time = models.DateTimeField()
    # name of the tournament. May be left blank
    name = models.CharField(max_length = 100, blank = True)
    # players participating in this tournament
    players = models.ManyToManyField(Player, related_name = "tournament_players")
    # ante from each player, in percent
    ante = models.IntegerField()
    # the number of points to take from the point pool for each player
    pool_points = models.IntegerField(default = 0)
    # the calculated total ante
    total_ante = models.IntegerField()
    # a written comment for this tournament
    comment = models.CharField(blank = True, max_length = 100000)

    def __unicode__(self):
        return u'%s_%s_%s_%s_%s_%s' % (self.name, self.finished, self.start_time,
                                       self.ante, self.pool_points, self.total_ante)

    def clean(self):
        pass

    class Meta:
        pass

# used for creating a new tournament
class TournamentCreateForm(ModelForm):
    class Meta:
        model = Tournament
        fields = (
            'start_time',
            'name',
            'players',
            'ante',
            'pool_points',
        )
        labels = {
            'start_time'   : _('Start time'),
            'name'         : _('Name'),
            'players'      : _('Players'),
            'ante'         : _('Ante (in %)'),
            'pool_points'  : _('Pool points unlocked'),
        }
        widgets = {
            'start_time' : DateTimeWidget(usel10n = True,
                                          bootstrap_version = 3,
                                          options = {'format' : 'yyyy-mm-dd hh:ii',
                                                     'weekStart' : '1'})
        }
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['players'].queryset = Player().active_players()

# used for editing a tournament
class TournamentEditForm(ModelForm):
    class Meta:
        model = Tournament
        fields = (
            'name',
            'total_ante',
            'finished',
        )
        labels = {
            'name'         : _('Name'),
            'total_ante'   : _('Total ante'),
            'finished'     : _('Finished'),
        }

# this is the number of points given to each placing in a tournament
class TournamentPlacingAnte(models.Model):
    # the tournament this ante belongs to
    tournament = models.ForeignKey(Tournament)
    # the placing it should be given to
    placing = models.IntegerField()
    # the ante this placing receives
    ante = models.IntegerField()
    # the player that got this placing
    player = models.ForeignKey(Player, null = True, blank = True)

    def __unicode__(self):
        return u'%s %s %s %s' % (self.tournament, self.placing, self.ante, self.player)

    def clean(self):
        pass

    class Meta:
        pass

class TournamentPlacingAnteForm(ModelForm):
    class Meta:
        model = TournamentPlacingAnte
        fields = (
            'placing',
            'ante',
        )
        labels = {
            'placing' : _('Placing'),
            'ante'    : _('Received ante'),
        }

TournamentPlacingAnteFormSet = inlineformset_factory(Tournament, TournamentPlacingAnte,
                                                       extra = 1, can_delete = False,
                                                       form = TournamentPlacingAnteForm)

class TournamentPlacingAnteSubmitForm(ModelForm):
    class Meta:
        model = TournamentPlacingAnte
        fields = (
            'placing',
            'ante',
            'player'
        )
        labels = {
            'placing' : _('Placing'),
            'ante'    : _('Received ante'),
            'player'  : _('Player'),
        }
    def __init__(self, *args, **kwargs):
        available_players = kwargs.pop('available_players', None)
        super(ModelForm, self).__init__(*args, **kwargs)

        if available_players:
            self.fields['player'].queryset = available_players

TournamentPlacingAnteSubmitFormSet = inlineformset_factory(Tournament, TournamentPlacingAnte,
                                        extra = 0, can_delete = False,
                                        form = TournamentPlacingAnteSubmitForm)

class PlayedGameManager(models.Manager):
    def last_game(self):
        return PlayedGame.objects.all().order_by('start_time').reverse().first()

# records a played game
class PlayedGame(models.Model):
    # the tournament this played game belongs to, if any
    tournament = models.ForeignKey(Tournament, null = True)
    # keeps track of whether this is a ranked game or not.
    # when tournament is not None, this should be False
    ranked = models.BooleanField(default = True)
    # the start time of the game
    start_time = models.DateTimeField()
    # the left player
    player_left = models.ForeignKey(Player, related_name="playedgame_player_left")
    # the right player
    player_right = models.ForeignKey(Player, related_name="playedgame_player_right")
    # winner of this game
    winner = models.ForeignKey(Player, related_name="winner", blank = True, null = True)
    # a written comment for this game
    comment = models.CharField(blank = True, max_length = 100000)

    objects = PlayedGameManager()

    def __unicode__(self):
        return u'%s %s vs %s, %s won' % (self.start_time, self.player_left, self.player_right, self.winner)

    def clean(self):
        pass

    class Meta:
        pass

class PlayedGameForm(ModelForm):
    class Meta:
        model = PlayedGame
        fields = (
            'start_time',
            'player_left',
            'player_right',
            'winner',
            'ranked'
        )
        labels = {
            'start_time'   : _('Start time'),
            'player_left'  : _('Left player'),
            'player_right' : _('Right player'),
            'winner'       : _('Winner'),
            'ranked'       : _('Ranked'),
        }
        widgets = {
            'start_time' : DateTimeWidget(usel10n = True,
                                          bootstrap_version = 3,
                                          options = {'format' : 'yyyy-mm-dd hh:ii',
                                                    'weekStart' : '1'})
        }

    def __init__(self, *args, **kwargs):
        available_players = kwargs.pop('available_players', None)
        super(ModelForm, self).__init__(*args, **kwargs)

        if available_players:
            self.fields['player_left'].queryset = available_players
            self.fields['player_right'].queryset = available_players

# a subgame to a game that has been played
class Subgame(models.Model):
    # the game this belongs to
    parent = models.ForeignKey(PlayedGame)
    # the map that was played.
    map_played = models.CharField(max_length = 100, blank = True)
    # the lives left for the left player at the end of the match
    pl_lives = models.IntegerField()
    # the lives left for the right player at the end of the match
    pr_lives = models.IntegerField()
    # the replay file for this game
    replay_file = models.FileField(blank=True, upload_to="replays/")

    def __unicode__(self):
        return u'%i - %i' % (self.pl_lives, self.pr_lives)

    def clean(self):
        pass

    class Meta:
        pass

class SubgameForm(ModelForm):
    class Meta:
        model = Subgame
        fields = (
            'map_played',
            'pl_lives',
            'pr_lives',
            'replay_file',
        )

        labels = {
            'map_played'   : _('Map played'),
            'pl_lives'     : _('Left player lives left'),
            'pr_lives'     : _('Right player lives left'),
            'replay_file'  : _('Replay file')
        }

SubgameFormSet = inlineformset_factory(PlayedGame, Subgame, max_num = 10, extra = 1,
                                       can_delete = False, form = SubgameForm)

# Keeps track of how ranking points etc was changed for a player.
# Used to keep track of before/after for games and tournaments
class PointsChanged(models.Model):
    # the player this belongs to
    player = models.ForeignKey(Player)
    # the tournament this belongs to. Both this and game may
    # not both be set (or both be null)
    tournament = models.ForeignKey(Tournament, blank = True, null = True)
    # the game this belongs to. Both this and tournament may
    # not both be set (or both be null)
    game = models.ForeignKey(PlayedGame, blank = True, null = True)
    # ranking points before match
    rp_before = models.IntegerField()
    # ranking points after match
    rp_after = models.IntegerField()
    # pool points before match
    pp_before = models.IntegerField()
    # pool points after match
    pp_after = models.IntegerField()

    def __unicode__(self):
        return u'%s_%s_%s_%s_%s_%s_%s' % (self.player, self.tournament,
                                          self.game, self.rp_before,
                                          self.rp_after, self.pp_before,
                                          self.pp_after)
    def clean(self):
        pass

    class Meta:
        pass

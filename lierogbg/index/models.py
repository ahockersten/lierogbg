from datetimewidget.widgets import DateTimeWidget
from django.db import models
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from index import fields

class Player(models.Model):
    name = models.CharField(max_length = 100)
    color = fields.ColorField()
    real_name = models.CharField(max_length = 100, blank = True)
    ranking_points = models.IntegerField(default = 1000)
    pool_points = models.IntegerField(default = 0)

    def __unicode__(self):
        return u'%s' % (self.name)

    def clean(self):
        pass

    class Meta:
        pass

# a game is divided into several sub-games
class PlayedGame(models.Model):
    start_time = models.DateTimeField()
    player_left = models.ForeignKey(Player, related_name="playedgame_player_left")
    player_right = models.ForeignKey(Player, related_name="playedgame_player_right")
    winner = models.ForeignKey(Player, related_name="winner", blank=True, null=True)
    # ranking points for left player, before match
    rp_pl_before = models.IntegerField()
    rp_pr_before = models.IntegerField()
    # ranking points for left player, after match
    rp_pl_after = models.IntegerField()
    rp_pr_after = models.IntegerField()
    # pool points for left player, before match
    pp_pl_before = models.IntegerField()
    pp_pr_before = models.IntegerField()
    # pool points for left player, after match
    pp_pl_after = models.IntegerField()
    pp_pr_after = models.IntegerField()

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
        )
        labels = {
            'start_time'   : _('Start time'),
            'player_left'  : _('Left player'),
            'player_right' : _('Right player'),
            'winner'       : _('Winner'),
        }
        widgets = {
            'start_time' : DateTimeWidget(usel10n = True,
                                          bootstrap_version=3,
                                          options= {'format' : 'yyyy-mm-dd hh:ii',
                                                    'weekStart' : '1'})
        }

class Subgame(models.Model):
    parent = models.ForeignKey(PlayedGame)
    map_played = models.CharField(max_length = 100, blank=True)
    pl_lives = models.IntegerField()
    pr_lives = models.IntegerField()
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

SubgameFormSet = inlineformset_factory(PlayedGame, Subgame, max_num=10, extra=1, can_delete=False, form=SubgameForm)

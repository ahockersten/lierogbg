from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

class Player(models.Model):
    name = models.CharField(max_length = 100)
    real_name = models.CharField(max_length = 100, blank = True)
    ranking_points = models.IntegerField(default = 1000)
    pool_points = models.IntegerField(default = 0)

    def __unicode__(self):
        return u'%s' % (self.name)

    def clean(self):
        pass

    class Meta:
        pass

class PlayedGame(models.Model):
    start_time = models.DateTimeField()
    player_left = models.ForeignKey(Player, related_name="player_left")
    player_right = models.ForeignKey(Player, related_name="player_right")
    winner = models.ForeignKey(Player, related_name="winner")
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

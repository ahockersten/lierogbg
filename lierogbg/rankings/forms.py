"""
Custom forms
"""
# pylint: disable=bad-super-call
from datetimewidget.widgets import DateTimeWidget
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from rankings import models
from .widgets import CalendarWidget

class TournamentCreateForm(ModelForm):
    """
    Form used for creating a new tournament.
    """
    class Meta:
        """
        Meta class for this form.
        """
        model = models.Tournament
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
            'start_time' : CalendarWidget()
        }
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['players'].queryset = models.Player.objects.active_players()

class TournamentEditForm(ModelForm):
    """
    Form used for editing a new tournament.
    """
    class Meta:
        """
        Meta class for this form.
        """
        model = models.Tournament
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

class TournamentPlacingAnteForm(ModelForm):
    """
    Form used for describing a tournament placing ante.
    """
    class Meta:
        """
        Meta class for this form.
        """
        model = models.TournamentPlacingAnte
        fields = (
            'placing',
            'ante',
        )
        labels = {
            'placing' : _('Placing'),
            'ante'    : _('Received ante'),
        }

TournamentPlacingAnteFormSet = inlineformset_factory(
    models.Tournament, models.TournamentPlacingAnte, extra=1,
    can_delete=False, form=TournamentPlacingAnteForm)

class TournamentPlacingAnteSubmitForm(ModelForm):
    """
    Form used for recording the result of a given tournament placing ante.
    """
    class Meta:
        """
        Meta class for this form.
        """
        model = models.TournamentPlacingAnte
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

TournamentPlacingAnteSubmitFormSet = inlineformset_factory(
    models.Tournament, models.TournamentPlacingAnte, extra=0,
    can_delete=False, form=TournamentPlacingAnteSubmitForm)

class SubgameForm(ModelForm):
    """
    Used for entering a Subgame.
    """
    class Meta:
        """
        Meta class for this form.
        """
        model = models.Subgame
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

SubgameFormSet = inlineformset_factory(models.PlayedGame, models.Subgame,
                                       max_num=10, extra=1, can_delete=False,
                                       form=SubgameForm)

class PlayedGameForm(ModelForm):
    """
    Used for entering results of a played game.
    """
    class Meta:
        """
        Meta class for this form.
        """
        model = models.PlayedGame
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
            'start_time' : CalendarWidget()
        }

    def __init__(self, *args, **kwargs):
        available_players = kwargs.pop('available_players', None)
        super(ModelForm, self).__init__(*args, **kwargs)

        if available_players:
            self.fields['player_left'].queryset = available_players
            self.fields['player_right'].queryset = available_players

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rankings import fields

class PlayerManager(models.Manager):
    def active_players(self):
        return Player.objects.all().filter(active=True)

# Describes a player. This is separate from the authentication
# system
class Player(models.Model):
    # displayed name
    name = models.CharField(max_length=100)
    # color used for the worm in the game
    color = fields.ColorField()
    # real name, optional
    real_name = models.CharField(max_length=100, blank=True)
    # current ranking points
    ranking_points = models.IntegerField(default=1000)
    # current pool points
    pool_points = models.IntegerField(default=0)
    # if the player is not active, it is not visible in the ranking table etc
    active = models.BooleanField(default=True)
    # a written comment for this player
    comment = models.CharField(blank=True, max_length=100000)

    objects = PlayerManager()

    # calculates the ante according to the given formula for a certain
    # ante percentage and a pool point unlock
    # returns a dictionary consisting of the ante, the new rp (without removing
    # the ante) and the new pp
    def calculate_ante_percentage(self, percentage, pool_points):
        rp = self.ranking_points
        pp = self.pool_points
        if (pp != 0):
            rp = self.ranking_points + min(self.pool_points, pool_points)
            pp = pp - min(pp, pool_points)
        player_ante = round((rp ** 2) * 0.001 * (percentage * 0.01))
        if player_ante == 0 and rp != 0:
            player_ante = 1
        tmp = {}
        tmp["ante"] = int(player_ante)
        tmp["rp"] = rp
        tmp["pp"] = pp
        return tmp

    # calculates the ante for a ranked match for this player
    # returns a dictionary consisting of the ante, the new rp (without removing
    # the ante) and the new pp
    def calculate_ranked_ante(self):
        return self.calculate_ante_percentage(2, 40)

    # returns all games that the Player p participated in
    def all_games(self):
        return PlayedGame.objects.all().filter(Q(player_left = self) |
                                               Q(player_right = self))

    # returns all games with this player that earned or lost them ranking points,
    # in other words: ranked and tournament games, but not unranked games
    def ranked_and_tournament_games(self, since):
        games = self.all_games().exclude(Q(ranked=False) &
                                         Q(tournament=None))
        if (since != None):
            return games.filter(start_time__gt=since)

    def total_points(self):
        return self.ranking_points + self.pool_points

    def __str__(self):
        return '%s' % (self.name)

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
    finished = models.BooleanField(default=False)
    # time and date when the tournament started
    start_time = models.DateTimeField()
    # name of the tournament. May be left blank
    name = models.CharField(max_length=100, blank=True)
    # players participating in this tournament
    players = models.ManyToManyField(Player, related_name="tournament_players")
    # ante from each player, in percent
    ante = models.IntegerField()
    # the number of points to take from the point pool for each player
    pool_points = models.IntegerField(default=0)
    # the calculated total ante
    total_ante = models.IntegerField()
    # a written comment for this tournament
    comment = models.CharField(blank=True, max_length=100000)

    # distributes points to all players in this tournament. It is an error to call this
    # without finished being set to true
    def distribute_points(self):
        # not allowed to distribute points for unfinished tournaments
        if not self.finished:
            raise ValueError
        tpas = self.tournament_placing_antes()
        for tpa in tpas:
            tpa.player.ranking_points = tpa.player.ranking_points + tpa.ante
            tpa.player.save()
            points_changed = PointsChanged.objects.all().filter(tournament=self,
                                                                player=tpa.player)[0]
            points_changed.rp_after = tpa.player.ranking_points
            points_changed.save()

    def games(self):
        return PlayedGame.objects.all().filter(tournament=self)

    def winner(self):
        try:
            return TournamentPlacingAnte.objects.all().filter(tournament=self).filter(placing=1)[0].player
        except:
            return None

    def tournament_placing_antes(self):
        return TournamentPlacingAnte.objects.all().filter(tournament=self)

    def __str__(self):
        return '%s_%s_%s_%s_%s_%s' % (self.name, self.finished,
                                      self.start_time, self.ante,
                                      self.pool_points, self.total_ante)

    def clean(self):
        pass

    class Meta:
        pass

# this is the number of points given to each placing in a tournament
class TournamentPlacingAnte(models.Model):
    # the tournament this ante belongs to
    tournament = models.ForeignKey(Tournament)
    # the placing it should be given to
    placing = models.IntegerField()
    # the ante this placing receives
    ante = models.IntegerField()
    # the player that got this placing
    player = models.ForeignKey(Player, null=True, blank=True)

    def __str__(self):
        return u'%s %s %s %s' % (self.tournament, self.placing, self.ante,
                                 self.player)

    def clean(self):
        pass

    class Meta:
        pass

class PlayedGameManager(models.Manager):
    # the last game that was played
    def last_game(self):
        return PlayedGame.objects.all().order_by('start_time').reverse().first()

# records a played game
class PlayedGame(models.Model):
    # the tournament this played game belongs to, if any
    tournament = models.ForeignKey(Tournament, null=True)
    # keeps track of whether this is a ranked game or not.
    # when tournament is not None, this should be False
    ranked = models.BooleanField(default=True)
    # the start time of the game
    start_time = models.DateTimeField()
    # the left player
    player_left = models.ForeignKey(Player, related_name="playedgame_player_left")
    # the right player
    player_right = models.ForeignKey(Player, related_name="playedgame_player_right")
    # winner of this game
    winner = models.ForeignKey(Player, related_name="winner", blank=True, null=True)
    # a written comment for this game
    comment = models.CharField(blank=True, max_length=100000)

    objects = PlayedGameManager()

    # returns all subgames played as a part of this game
    def subgames(self):
        return Subgame.objects.all().filter(parent=self)

    def __str__(self):
        return '%s %s vs %s, %s won' % (self.start_time, self.player_left,
                                        self.player_right, self.winner)

    def clean(self):
        pass

    class Meta:
        pass

# a subgame to a game that has been played
class Subgame(models.Model):
    # the game this belongs to
    parent = models.ForeignKey(PlayedGame)
    # the map that was played.
    map_played = models.CharField(max_length=100, blank=True)
    # the lives left for the left player at the end of the match
    pl_lives = models.IntegerField()
    # the lives left for the right player at the end of the match
    pr_lives = models.IntegerField()
    # the replay file for this game
    replay_file = models.FileField(blank=True, upload_to="replays/")

    def __str__(self):
        return u'%i - %i' % (self.pl_lives, self.pr_lives)

    def clean(self):
        pass

    class Meta:
        pass

# Keeps track of how ranking points etc was changed for a player.
# Used to keep track of before/after for games and tournaments
class PointsChanged(models.Model):
    # the player this belongs to
    player = models.ForeignKey(Player)
    # the tournament this belongs to. Both this and game may
    # not both be set (or both be null)
    tournament = models.ForeignKey(Tournament, blank=True, null=True)
    # the game this belongs to. Both this and tournament may
    # not both be set (or both be null)
    game = models.ForeignKey(PlayedGame, blank=True, null=True)
    # ranking points before match
    rp_before = models.IntegerField()
    # ranking points after match
    rp_after = models.IntegerField()
    # pool points before match
    pp_before = models.IntegerField()
    # pool points after match
    pp_after = models.IntegerField()

    def __str__(self):
        return u'%s_%s_%s_%s_%s_%s_%s' % (self.player, self.tournament,
                                          self.game, self.rp_before,
                                          self.rp_after, self.pp_before,
                                          self.pp_after)
    def clean(self):
        pass

    class Meta:
        pass

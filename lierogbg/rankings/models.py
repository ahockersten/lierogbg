"""
Models used in the rankings
"""
from django.db import models
from django.db.models import Q
from django.forms import ValidationError
from rankings import fields


class PlayerManager(models.Manager):
    """
    Model manager for Player.
    """
    def active_players(self):
        """
        Returns all active players.
        """
        return self.all().filter(active=True)


class Player(models.Model):
    """
    Describes a player. This is separate from the authentication system
    """
    # displayed name
    name = models.CharField(max_length=100)
    # color used for the worm in the game
    color = fields.ColorField()
    # real name, optional
    real_name = models.CharField(max_length=100, blank=True)
    # the ranking points this player started with. For new players, this is
    # always 0.
    start_ranking_points = models.IntegerField(default=0)
    # the pool points this player started with. For new players, this is
    # always 1000.
    start_pool_points = models.IntegerField(default=1000)
    # if the player is not active, it is not visible in the ranking table etc
    active = models.BooleanField(default=True)
    # a written comment for this player
    comment = models.CharField(blank=True, max_length=100000)

    objects = PlayerManager()

    @property
    def ranking_points(self):
        """
        Current ranking points for this player
        """
        latest_pcs = self.get_latest_pcs()
        if latest_pcs is None:
            return self.start_ranking_points
        return latest_pcs.rp_after

    @property
    def pool_points(self):
        """
        Current pool points for this player
        """
        latest_pcs = self.get_latest_pcs()
        if latest_pcs is None:
            return self.start_pool_points
        return latest_pcs.pp_after

    def get_latest_pcs(self):
        """
        Returns the latest PointsChanged that applied to this player
        """
        try:
            last_game_with_player = PlayedGame.objects.filter(
                Q(player_left=self) | Q(player_right=self)). \
                latest('start_time')
        except PlayedGame.DoesNotExist:
            last_game_with_player = None
        try:
            last_tournament_with_player = Tournament.objects.filter(
                players=self).latest('start_time')
        except Tournament.DoesNotExist:
            last_tournament_with_player = None
        if last_game_with_player is None and \
           last_tournament_with_player is None:
            return None
        elif last_game_with_player is None:
            pcs = PointsChanged.objects.filter(
                tournament=last_tournament_with_player).filter(player=self)
        elif last_tournament_with_player is None:
            pcs = PointsChanged.objects.filter(
                game=last_game_with_player).filter(player=self)
        elif last_game_with_player.start_time < \
                last_tournament_with_player.start_time:
            pcs = PointsChanged.objects.filter(
                game=last_game_with_player).filter(player=self)
        else:
            pcs = PointsChanged.objects.filter(
                tournament=last_tournament_with_player).filter(player=self)
        return pcs[0]

    def validate(self):
        """
        Ensures that a player's match history is correct. Does this by going
        through all the matches and tournaments for the player, in order,
        and checking that their RP/PP before/after are all correct.
        """
        pcs = PointsChanged.objects.filter(player=self)
        sorted_pcs = sorted(pcs, key=lambda pc: pc.game.start_time if pc.game
                            else pc.tournament.start_time)
        if sorted_pcs == []:
            return "No matches played"
        rp_last = self.start_ranking_points
        pp_last = self.start_pool_points
        for pc in sorted_pcs:
            if pc.rp_before != rp_last or \
               pc.pp_before != pp_last:
                returned = pc.game if pc.game is not None else pc.tournament
                return "Failed for {match}".format(match=str(returned))
            rp_last = pc.rp_after
            pp_last = pc.pp_after
        return "No errors found"

    def calculate_ante_percentage(self, percentage, pool_points):
        """
        Calculates the ante according to the given formula for a certain
        ante percentage and a pool point unlock returns a dictionary
        consisting of the ante, the new rp (without removing the ante)
        and the new pp.
        """
        rp = self.ranking_points
        pp = self.pool_points
        if pp != 0:
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

    def calculate_ranked_ante(self):
        """
        Calculates the ante for a ranked match for this player
        returns a dictionary consisting of the ante, the new rp
        (without removing the ante) and the new pp.
        """
        return self.calculate_ante_percentage(2, 40)

    def all_games(self):
        """
        Returns all games that the Player participated in
        """
        return PlayedGame.objects.filter(Q(player_left=self) |
                                         Q(player_right=self))

    def ranked_and_tournament_games(self, since):
        """
        Returns all games with this player that earned or lost
        them ranking points, in other words: ranked and tournament
        games, but not unranked games.
        """
        games = self.all_games().exclude(Q(ranked=False) &
                                         Q(tournament=None))
        if since is not None:
            return games.filter(start_time__gt=since)

    def total_points(self):
        """
        Returns the sum of all points belonging to this player.
        """
        return self.ranking_points + self.pool_points

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        """
        Meta class deciding ordering for this model.
        """
        ordering = ['name']


class Tournament(models.Model):
    """
    Describes a tournament. When initially created, it takes
    the ante from and adds pool points to all players. When
    it is recorded as finished, "finished" is set to True and
    it hands out the ante to the winners.
    """
    # when True, this tournament has ended and points from it have been
    # recorded
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

    def distribute_points(self):
        """
        Distributes points to all players in this tournament.
        It is an error to call this without finished being set
        to true.
        """
        # not allowed to distribute points for unfinished tournaments
        if not self.finished:
            raise ValueError
        tpas = self.tournament_placing_antes()
        for tpa in tpas:
            tpa.player.ranking_points = tpa.player.ranking_points + tpa.ante
            tpa.player.save()
            pcs = PointsChanged.objects.all()
            points_changed = pcs.filter(tournament=self, player=tpa.player)[0]
            points_changed.rp_after = tpa.player.ranking_points
            points_changed.save()

    def games(self):
        """
        Returns all played games in this tournament.
        """
        return PlayedGame.objects.all().filter(tournament=self)

    def winner(self):
        """
        Returns the winner of this tournament, or None if
        there is no winner.
        """
        tpas = TournamentPlacingAnte.objects.all()
        try:
            return tpas.filter(tournament=self).filter(placing=1)[0].player
        except IndexError:
            return None

    def tournament_placing_antes(self):
        """
        Returns all tournament placing antes belonging to
        this tournament.
        """
        return TournamentPlacingAnte.objects.all().filter(tournament=self)

    def __str__(self):
        return '%s_%s_%s_%s_%s_%s' % (self.name, self.finished,
                                      self.start_time, self.ante,
                                      self.pool_points, self.total_ante)


class TournamentPlacingAnte(models.Model):
    """
    This is the number of points given to each placing in
    a tournament.
    """
    # the tournament this ante belongs to
    tournament = models.ForeignKey(Tournament)
    # the placing it should be given to
    placing = models.IntegerField()
    # the ante this placing receives
    ante = models.IntegerField()
    # the player that got this placing
    player = models.ForeignKey(Player, null=True, blank=True)

    def __str__(self):
        return '%s %s %s %s' % (self.tournament, self.placing, self.ante,
                                self.player)


class PlayedGameManager(models.Manager):
    """
    Manager for the PlayedGame class
    """
    def last_game(self):
        """
        The last game that was played
        """
        return self.all().order_by('start_time').reverse().first()


class PlayedGame(models.Model):
    """
    Records a played game
    """
    # the tournament this played game belongs to, if any
    tournament = models.ForeignKey(Tournament, null=True)
    # keeps track of whether this is a ranked game or not.
    # when tournament is not None, this should be False
    ranked = models.BooleanField(default=True)
    # the start time of the game
    start_time = models.DateTimeField()
    # the left player
    player_left = models.ForeignKey(Player,
                                    related_name="playedgame_player_left")
    # the right player
    player_right = models.ForeignKey(Player,
                                     related_name="playedgame_player_right")
    # winner of this game
    winner = models.ForeignKey(Player, related_name="winner",
                               blank=True, null=True)
    # a written comment for this game
    comment = models.CharField(blank=True, max_length=100000)

    objects = PlayedGameManager()

    def subgames(self):
        """
        Returns all subgames played as a part of this game.
        """
        return Subgame.objects.all().filter(parent=self)

    def __str__(self):
        return '%s %s vs %s, %s won' % (self.start_time, self.player_left,
                                        self.player_right, self.winner)


class Subgame(models.Model):
    """
    A subgame to a game that has been played
    """
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
        return '%i - %i' % (self.pl_lives, self.pr_lives)

    def clean(self):
        """
        Custom clean. Make sure pl_lives and pr_lives are positive
        """
        if self.pl_lives < 0:
            raise ValidationError('Player left lives may not be less than 0')
        if self.pr_lives < 0:
            raise ValidationError('Player right lives may not be less than 0')


class PointsChanged(models.Model):
    """
    Keeps track of how ranking points etc was changed for a player.
    Used to keep track of before/after for games and tournaments.
    """
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
        return '%s_%s_%s_%s_%s_%s_%s' % (self.player, self.tournament,
                                         self.game, self.rp_before,
                                         self.rp_after, self.pp_before,
                                         self.pp_after)

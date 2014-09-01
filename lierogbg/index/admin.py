from django.contrib import admin
from index.models import Player, PlayedGame, Subgame, Tournament, TournamentPlacingAnte, PointsChanged

class PlayerAdmin(admin.ModelAdmin):
    pass

class PlayedGameAdmin(admin.ModelAdmin):
    pass

class SubgameAdmin(admin.ModelAdmin):
    pass

class TournamentAdmin(admin.ModelAdmin):
    pass

class TournamentPlacingAnteAdmin(admin.ModelAdmin):
    pass

class PointsChangedAdmin(admin.ModelAdmin):
    pass

admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayedGame, PlayedGameAdmin)
admin.site.register(Subgame, SubgameAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(TournamentPlacingAnte, TournamentPlacingAnteAdmin)
admin.site.register(PointsChanged, PointsChangedAdmin)

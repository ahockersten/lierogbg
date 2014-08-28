from django.contrib import admin
from index.models import Player, PlayedGame, Subgame

class PlayerAdmin(admin.ModelAdmin):
    pass

class PlayedGameAdmin(admin.ModelAdmin):
    pass

class SubgameAdmin(admin.ModelAdmin):
    pass

admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayedGame, PlayedGameAdmin)
admin.site.register(Subgame, SubgameAdmin)

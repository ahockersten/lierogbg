from django.contrib import admin
from index.models import Player, PlayedGame

class PlayerAdmin(admin.ModelAdmin):
    pass

class PlayedGameAdmin(admin.ModelAdmin):
    pass

admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayedGame, PlayedGameAdmin)

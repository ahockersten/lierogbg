from django.contrib import admin
from index.models import Player

class PlayerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Player, PlayerAdmin)

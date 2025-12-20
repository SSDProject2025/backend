from django.contrib import admin
from fiordispino.models import Genre, User, Game, GamesToPlay, GamePlayed
from fiordispino.permissions import (
    forbid_add_permission,
    forbid_change_permission
)

admin.site.register(Genre)
admin.site.register(User)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    # These fields are updated automatically based on user ratings in GamesPlayed
    readonly_fields = ('global_rating', 'rating_count')


@admin.register(GamesToPlay)
class GamesToPlayAdmin(admin.ModelAdmin):
    """
    Admin configuration for the 'Backlog' list.
    Admins can view and delete entries, but cannot manually add or edit them.
    """
    has_add_permission = forbid_add_permission
    has_change_permission = forbid_change_permission

    # Admins are now allowed to delete entries to manage the database content
    def has_delete_permission(self, request, obj=None):
        return True

    list_display = ('__str__', 'owner', 'game')


@admin.register(GamePlayed)
class GamePlayedAdmin(admin.ModelAdmin):
    """
    Admin configuration for the 'Played' list.
    Admins can view and delete entries, but cannot manually add or edit them.
    """
    has_add_permission = forbid_add_permission
    has_change_permission = forbid_change_permission

    # Admins are now allowed to delete entries (e.g., to remove fake/troll reviews)
    def has_delete_permission(self, request, obj=None):
        return True

    list_display = ('__str__', 'owner', 'game', 'rating')
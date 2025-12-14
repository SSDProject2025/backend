from django.contrib import admin

from fiordispino.models import *
from fiordispino.permissions import *

admin.site.register(Genre)
admin.site.register(User)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    # these fields can only change when a user make some action on GamesPlayed
    readonly_fields = ('global_rating', 'rating_count')

# The admin should just visualize libraries, not create/edit/delete
@admin.register(GamesToPlay)
class GamesToPlayAdmin(admin.ModelAdmin):
    has_add_permission = forbid_add_permission
    has_change_permission = forbid_change_permission

    # why block also delete permission? Because it make no sense to delete a library! The app become unusable for the user
    # if a user does strange stuff just ban them
    has_delete_permission = forbid_delete_permission

    list_display = ('__str__',)


@admin.register(GamePlayed)
class GamePlayedAdmin(admin.ModelAdmin):
    has_add_permission = forbid_add_permission
    has_change_permission = forbid_change_permission

    # why block also delete permission? Because it make no sense to delete a library! The app become unusable for the user
    # if a user does strange stuff just ban them
    has_delete_permission = forbid_delete_permission

    list_display = ('__str__',)


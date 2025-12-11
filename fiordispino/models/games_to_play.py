from django.contrib.auth import get_user_model
from django.db import models

"""
Strong refactor: this is no more a list of games but rather a single entity, so that the fact that a user cannot have more than 1 list of games to play
is implicit
"""
class GamesToPlay(models.Model):

    # A library is owned by just 1 user. If said user deletes his profile delete the library too
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='games_to_play'  # so that you can do user.games_to_play.all()
    )
    game = models.ForeignKey(
        'fiordispino.game',
        on_delete=models.CASCADE,
        related_name='to_be_played_by_user'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # so that a user can add a game to play at most 1 time
        unique_together = ('owner', 'game')
        verbose_name = "Game to play"
        verbose_name_plural = "Games to play"

    def __str__(self):
        return f"{self.owner.username} wants to play {self.game.title}"
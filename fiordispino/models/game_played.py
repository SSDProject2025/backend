from django.db import models

from django.conf import settings
from fiordispino.core.validators import validate_vote

"""
having an entity that links a game as played by one user it's easier to handle compared to an entity that links a list of games to a user
in this way the fact that a user can have just one list of games is implicit by the fact that in the db is not actually a list!
"""
class GamePlayed(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='played_games'  # so that you can do user.played_games.all()
    )
    game = models.ForeignKey(
        'fiordispino.game',
        on_delete=models.CASCADE,
        related_name='played_by_user'
    )

    rating = models.PositiveIntegerField(validators=[validate_vote])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # so that a user can add a game to play at most 1 time
        unique_together = ('owner', 'game')
        verbose_name = "Game played"
        verbose_name_plural = "Games played"

    def __str__(self):
        return f"{self.game.title} played by {self.owner.username} and rated {self.rating}/10"
from django.contrib.auth import get_user_model
from django.db import models

class GamesToPlay(models.Model):

    # A library is owned by just 1 user. If said user deletes his profile delete the library too
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    games = models.ManyToManyField('Game', related_name='games_to_play')

    def __str__(self):
        return f"{self.owner.username}'s games to play"
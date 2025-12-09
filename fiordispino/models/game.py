from django.db import models

from fiordispino.models import Genre
from fiordispino.core.validators import *


class Game(models.Model):
    box_art = models.ImageField() # todo: you should give it a path to store the images. Better to specify it in the .env
    description = models.TextField(validators=[validate_game_description])
    title = models.TextField(validators=[validate_title])
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE) # todo: this has to become a list
    pegi = models.IntegerField(validators=[validate_pegi])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
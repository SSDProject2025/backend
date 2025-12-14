from django.db import models

from fiordispino.models import Genre
from fiordispino.core.validators import *


import os

def build_path(instance, filename):
    # instance: game object to be saved
    # filename: name of the image

    # extract extension
    ext = filename.split('.')[-1]

    # create the file name
    # Eg: "The Legend of Zelda" becomes "the_legend_of_zelda_cover.jpg"
    new_filename = f"{instance.title.replace(' ', '_').lower()}_cover.{ext}"

    return os.path.join('games', 'covers', new_filename)

class Game(models.Model):
    box_art = models.ImageField(upload_to=build_path)
    description = models.TextField(validators=[validate_game_description])
    title = models.TextField(validators=[validate_title])
    global_rating = models.FloatField(default=0.0, validators=[validate_global_rating])

    # to count how many players reviewed it. No need for custom validation, it's implicit thanks to PositiveInteger
    rating_count = models.PositiveIntegerField(default=0)

    # many-to-many relation: a game has (can have) more than 1 genre; a genre is (can be) associated to more than 1 game
    genres = models.ManyToManyField(Genre, related_name='games')

    pegi = models.IntegerField(validators=[validate_pegi])
    release_date = models.DateField() # do we keep it?

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from fiordispino.models import Game, Genre
from fiordispino.models.game import build_path
import os



class GameModelTest(TestCase):

    def setUp(self):
        # create mock data for the tests
        self.genre_action = Genre.objects.create(name="Action")
        self.genre_rpg = Genre.objects.create(name="RPG")

    def test_game_creation_and_str_method(self):
        game = Game.objects.create(
            title="The Legend of Zelda",
            description="Un gioco di avventura fantastico.",
            pegi=12,
            release_date=date(2017, 3, 3),
            box_art="games/covers/zelda.jpg"  # fake path
        )

        # need to add it manually because it is an entity in the db
        game.genres.add(self.genre_action)

        self.assertEqual(game.title, "The Legend of Zelda")
        self.assertEqual(str(game), "The Legend of Zelda")
        self.assertEqual(game.pegi, 12)

        # timestamp verification
        self.assertIsNotNone(game.created_at)
        self.assertIsNotNone(game.updated_at)

    def test_game_genres_relationship(self):

        game = Game.objects.create(
            title="Elden Ring",
            description="Apparently, a very hard game",
            pegi=16,
            release_date=date(2022, 2, 25)
        )

        # add different genres to tests that it actually accepts many field
        game.genres.add(self.genre_action, self.genre_rpg)

        self.assertEqual(game.genres.count(), 2)

        self.assertIn(self.genre_action, game.genres.all())
        self.assertIn(self.genre_rpg, game.genres.all())

    def test_game_update_updates_timestamp(self):
        game = Game.objects.create(
            title="Old Title",
            description="Desc...",
            pegi=3,
            release_date=date(2020, 1, 1)
        )
        original_updated_at = game.updated_at

        game.title = "New Title"
        game.save()

        self.assertNotEqual(game.updated_at, original_updated_at)

    def test_game_validation_fails_with_invalid_data(self):

        invalid_game = Game(
            title="",
            description=">>>>@@######",
            pegi=-5,
            release_date=date.today()
        )

        # full_clean() is the method that actually runs the validators
        with self.assertRaises(ValidationError):
            invalid_game.full_clean()

    def test_box_art_path_logic(self):
        # this method is not actually part of the game model, however since it is fundamental for its logic I decided to include it here
        game = Game(title="The Legend of Zelda")

        original_filename = "zelda.png"

        generated_path = build_path(game, original_filename)

        expected_filename = "the_legend_of_zelda_cover.png"
        expected_path = os.path.join('games', 'covers', expected_filename)

        self.assertEqual(generated_path, expected_path)
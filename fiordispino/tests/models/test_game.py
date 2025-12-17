import os
from datetime import date
import pytest
from django.core.exceptions import ValidationError
from fiordispino.core.exceptions import InvalidImageFormatException
from mixer.backend.django import mixer

from fiordispino.models import Game, Genre, GamePlayed
from fiordispino.models.game import build_path
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGameModel:

    @pytest.fixture
    def genre_action(self):
        return mixer.blend(Genre, name="Action")

    @pytest.fixture
    def genre_rpg(self):
        return mixer.blend(Genre, name="RPG")

    def test_game_creation_and_str_method(self, genre_action):
        # mixer is capable of generating data, but it's better to hardcode some field to avoid problems with validators
        game = mixer.blend(Game,
                           title="The Legend of Zelda",
                           pegi=12,
                           release_date=date(2017, 3, 3),
                           box_art="games/covers/zelda.jpg"
                           )

        game.genres.add(genre_action)

        assert game.title == "The Legend of Zelda"
        assert str(game) == "The Legend of Zelda"
        assert game.pegi == 12

        assert game.created_at is not None
        assert game.updated_at is not None

    def test_game_genres_relationship(self, genre_action, genre_rpg):
        game = mixer.blend(Game, title="Elden Ring")

        game.genres.add(genre_action, genre_rpg)

        assert game.genres.count() == 2
        assert genre_action in game.genres.all()
        assert genre_rpg in game.genres.all()

    def test_game_update_updates_timestamp(self):
        game = mixer.blend(Game, title="Red Dead Redemption II")
        original_updated_at = game.updated_at

        game.title = "New Title"
        game.save()

        assert game.updated_at != original_updated_at

    def test_game_validation_fails_with_invalid_data(self):
        invalid_game = Game(
            title="",  # (invalid)
            description="Bad",
            pegi=-5,  # (invalid)
            release_date=date.today()
        )

        with pytest.raises(ValidationError):
            invalid_game.full_clean()

    def test_box_art_path_logic(self):
        game = Game(title="The Legend of Zelda")
        original_filename = "zelda.png"

        generated_path = build_path(game, original_filename)

        expected_filename = "the_legend_of_zelda_cover.png"
        expected_path = os.path.join('games', 'covers', expected_filename)

        assert generated_path == expected_path

    def test_game_rating_count_cant_be_negative(self):
        game = Game(
            title="Dragon quest V",
            description="classic fantasy rpg",
            pegi=12,
            release_date=date(2017, 3, 3),
            global_rating=10.0,
            rating_count=-1
        )

        with pytest.raises(ValidationError):
            game.full_clean()

    def test_game_global_rating_cant_have_more_than_three_digits(self):
        game = Game(
            title="The Legend of Zelda",
            description="classic fantasy rpg",
            pegi=12,
            release_date=date(2017, 3, 3),
            global_rating=10.07,
            rating_count=2
        )

        with pytest.raises(ValidationError):
            game.full_clean()

    def test_game_global_rating_works_with_valid_values(self):
        game = Game(
            title="The Legend of Zelda",
            description="classic fantasy rpg",
            pegi=12,
            release_date=date(2017, 3, 3),
            global_rating=10.1,
            rating_count=2
        )

    @pytest.mark.parametrize("ratings_list, expected_global_rating", [
        ([10, 10, 8], 9.3),  # avg: 9.3333... -> rounded to: 9.3
        ([1, 2], 1.5),  # 1.5 -> 1.5
        ([10, 10], 10.0),  # 10.0 -> 10.0
        ([5, 6, 7], 6.0),  # 6.0 -> no rounding
        ([1, 1, 2], 1.3),  # 1.3333... -> 1.3
    ])
    def test_game_global_rating_is_always_rounded_correctly(self, games, ratings_list, expected_global_rating):
        game = games[0]

        # given the fact that the game is fixed I need to create a different user for each value because a user can add a game as played just 1 time
        for rating in ratings_list:
            player = mixer.blend(get_user_model())
            GamePlayed.objects.create(owner=player, game=game, rating=rating)

        game.refresh_from_db()

        assert float(game.global_rating) == expected_global_rating

    def test_game_validation_fails_with_non_jpg_box_art(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        png_file = SimpleUploadedFile(
            name='test_image.png',
            content=b'fake image content',
            content_type='image/png'
        )

        game = Game(
            title="Cool game",
            description="Testing invalid format",
            pegi=3,
            release_date=date(2020, 1, 1),
            box_art=png_file
        )

        with pytest.raises(ValidationError):
            game.full_clean()
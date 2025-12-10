import os
from datetime import date
import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer

from fiordispino.models import Game, Genre
from fiordispino.models.game import build_path


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
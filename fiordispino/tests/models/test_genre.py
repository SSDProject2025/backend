import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from fiordispino.models import Genre

@pytest.mark.django_db
class TestGenreModel:

    def test_genre_creation_and_str_method(self):
        genre = mixer.blend(Genre, name="Fantasy")

        assert genre.name == "Fantasy"
        assert str(genre) == "Fantasy"

        assert genre.created_at is not None
        assert genre.updated_at is not None

    def test_genre_update_updates_timestamp(self):
        genre = mixer.blend(Genre)
        original_updated_at = genre.updated_at

        genre.name = "Survival Horror"
        genre.save()

        assert genre.updated_at != original_updated_at

    def test_genre_validation_is_connected(self):
        invalid_genre = Genre(name="")

        with pytest.raises(ValidationError):
            invalid_genre.full_clean()
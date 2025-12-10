import pytest

from fiordispino.core.validators import validate_genre
from fiordispino.core.exceptions import GenreException,NoGenreProvided,GenreTooLong

class TestValidateGenre:

    def test_validate_genre_should_fail_on_empty_genre(self):
        with pytest.raises(NoGenreProvided):
            validate_genre('')

    def test_validate_genre_should_fail_with_numbers(self):
        with pytest.raises(GenreException):
            validate_genre('genre42')

    def test_validate_genre_should_fail_with_special_characters(self):
        with pytest.raises(GenreException):
            validate_genre('genre!!!!')


    def test_validate_genre_should_fail_with_genre_too_long(self):
        with pytest.raises(GenreTooLong):
            validate_genre('a'*101)

    @pytest.mark.parametrize("genre", [
        "rpg", "fantasy", "dark fantasy", "fps", "horror"
    ])
    def test_validate_genre_success(self, genre):
        validate_genre(genre)
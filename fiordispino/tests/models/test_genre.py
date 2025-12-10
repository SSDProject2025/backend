from django.test import TestCase
from django.core.exceptions import ValidationError
from fiordispino.models.genre import Genre


class GenreModelTest(TestCase):

    def test_genre_creation_and_str_method(self):
        genre = Genre.objects.create(name="Fantasy")

        self.assertEqual(genre.name, "Fantasy")
        self.assertEqual(str(genre), "Fantasy")

        self.assertIsNotNone(genre.created_at)
        self.assertIsNotNone(genre.updated_at)

    def test_genre_update_updates_timestamp(self):
        genre = Genre.objects.create(name="Horror")
        original_updated_at = genre.updated_at

        genre.name = "Survival Horror"
        genre.save()

        self.assertNotEqual(genre.updated_at, original_updated_at)

    def test_genre_validation_is_connected(self):
        invalid_genre = Genre(name="")

        with self.assertRaises(ValidationError):
            invalid_genre.full_clean()
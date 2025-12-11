import time
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from fiordispino.models import GamePlayed
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGamePlayed:

    def test_str_representation(self, user, games):
        """
        Test that the string representation includes the game title,
        the username, and the specific rating.
        """
        game = games[0]
        rating = 8
        entry = GamePlayed.objects.create(owner=user, game=game, rating=rating)

        expected_str = f"{game.title} played by {user.username} and rated {rating}/10"
        assert str(entry) == expected_str

    def test_uniqueness_constraint(self, user, games):
        """
        Test that a user cannot add the same game to the 'played' list more than once.
        Expects an IntegrityError.
        """
        game = games[0]

        # Create the first entry
        GamePlayed.objects.create(owner=user, game=game, rating=7)

        # Attempt to create a duplicate entry
        with pytest.raises(IntegrityError):
            GamePlayed.objects.create(owner=user, game=game, rating=9)

    def test_rating_validation(self, user, games):
        """
        Test that the rating validator is working.
        Note that it enforces a discrete range from 1 to 10
        """
        game = games[0]

        entry = GamePlayed(owner=user, game=game, rating=11)

        with pytest.raises(ValidationError):
            entry.full_clean()

    def test_different_users_can_add_same_game(self, games):
        """
        Test that two different users can mark the same game as played.
        """
        user1 = mixer.blend(User)
        user2 = mixer.blend(User)
        game = games[0]

        entry1 = GamePlayed.objects.create(owner=user1, game=game, rating=8)
        entry2 = GamePlayed.objects.create(owner=user2, game=game, rating=6)

        assert entry1.pk != entry2.pk
        assert GamePlayed.objects.count() == 2

    def test_timestamps_logic(self, user, games):
        """
        Test that created_at is set on creation and updated_at changes on save.
        """
        entry = GamePlayed.objects.create(owner=user, game=games[0], rating=5)

        original_created_at = entry.created_at
        original_updated_at = entry.updated_at

        assert original_created_at is not None
        assert original_updated_at is not None

        # Sleep briefly to ensure the timestamp actually changes
        time.sleep(0.01)

        # Update the object (e.g., change rating) and save
        entry.rating = 6
        entry.save()

        # Refresh from DB to get the DB-generated timestamps
        entry.refresh_from_db()

        # created_at MUST remain the same
        assert entry.created_at == original_created_at

        # updated_at MUST be greater than the original
        assert entry.updated_at > original_updated_at

    def test_cascade_delete_game(self, user, games):
        """
        Test that if a Game is deleted, the GamePlayed entry is also deleted (Cascade).
        """
        game = games[0]
        GamePlayed.objects.create(owner=user, game=game, rating=9)

        assert GamePlayed.objects.count() == 1

        # Delete the game
        game.delete()

        # The relation should be gone
        assert GamePlayed.objects.count() == 0

    def test_cascade_delete_user(self, user, games):
        """
        Test that if a User is deleted, their GamePlayed entries are also deleted (Cascade).
        """
        GamePlayed.objects.create(owner=user, game=games[0], rating=9)

        assert GamePlayed.objects.count() == 1

        # Delete the user
        user.delete()

        # The list should be gone
        assert GamePlayed.objects.count() == 0
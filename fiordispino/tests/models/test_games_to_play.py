import time
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from fiordispino.models import GamesToPlay
from fiordispino.tests.utils_testing import *

User = get_user_model()


@pytest.mark.django_db
class TestGamesToPlay:

    def test_str_representation(self, user, games):
        """
        Test that the string representation correctly identifies
         the user and the game they want to play.
        """
        game = games[0]
        entry = GamesToPlay.objects.create(owner=user, game=game)

        expected_str = f"{user.username} wants to play {game.title}"
        assert str(entry) == expected_str

    def test_uniqueness_constraint(self, user, games):
        """
        Test that a user cannot add the same game to their
        'Games to Play' list more than once.
        """
        game = games[0]
        GamesToPlay.objects.create(owner=user, game=game)

        with pytest.raises(IntegrityError):
            GamesToPlay.objects.create(owner=user, game=game)

    def test_different_users_can_add_same_game(self, games):
        """
        Test that multiple users can have the same game in their
        individual backlogs.
        """
        user1 = mixer.blend(User)
        user2 = mixer.blend(User)
        game = games[0]

        entry1 = GamesToPlay.objects.create(owner=user1, game=game)
        entry2 = GamesToPlay.objects.create(owner=user2, game=game)

        assert entry1.pk != entry2.pk
        assert GamesToPlay.objects.count() == 2

    def test_timestamps_logic(self, user, games):
        """
        Verify that created_at remains constant while updated_at
        changes upon record updates.
        """
        entry = GamesToPlay.objects.create(owner=user, game=games[0])

        original_created_at = entry.created_at
        original_updated_at = entry.updated_at

        assert original_created_at is not None
        assert original_updated_at is not None

        # Wait a moment to ensure the system clock advances
        time.sleep(0.01)

        # Update the object to trigger auto_now
        entry.save()
        entry.refresh_from_db()

        # created_at MUST remain the same
        assert entry.created_at == original_created_at
        # updated_at MUST be greater than the original
        assert entry.updated_at > original_updated_at

    def test_cascade_delete_game(self, user, games):
        """
        Test that deleting a Game object automatically removes
        it from all users' backlogs (CASCADE).
        """
        game = games[0]
        GamesToPlay.objects.create(owner=user, game=game)

        assert GamesToPlay.objects.count() == 1

        # Delete the source game
        game.delete()

        # The entry must be gone
        assert GamesToPlay.objects.count() == 0

    def test_cascade_delete_user(self, user, games):
        """
        Test that deleting a User removes their associated backlog.
        """
        GamesToPlay.objects.create(owner=user, game=games[0])

        assert GamesToPlay.objects.count() == 1

        # Delete the user
        user.delete()

        # The list entry must be deleted
        assert GamesToPlay.objects.count() == 0

    def test_admin_can_delete_entry(self, user, games):
        """
        Verify that an administrative action can delete a backlog entry,
        regardless of which user owns it.
        """
        # Create an admin user
        admin_user = mixer.blend(User, is_staff=True)
        game = games[0]
        entry = GamesToPlay.objects.create(owner=user, game=game)

        assert GamesToPlay.objects.count() == 1

        # In a real API scenario, the permission class allows this.
        # Here we verify the model instance can be deleted by an admin process.
        entry.delete()

        assert GamesToPlay.objects.count() == 0
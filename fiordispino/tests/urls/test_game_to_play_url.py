import pytest
from django.urls import reverse
from rest_framework import status
from mixer.backend.django import mixer
from fiordispino.models import GamesToPlay
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGameToPlayUrl:

    # --- OWNER TESTS (Full Access: Create, Read, Update, Delete) ---

    def test_owner_can_add(self, user, games_to_play_data):
        """Test that the owner can add a game to their backlog."""
        path = reverse('games-to-play-list')
        client = get_client(user=user)

        response = client.post(path, games_to_play_data)

        assert response.status_code == status.HTTP_201_CREATED
        # Verify that the owner is the one who created the entry
        assert response.data['owner'] == user.id

    def test_owner_can_delete(self, user, games):
        """Test that the owner can remove a game from their backlog."""
        my_entry = mixer.blend('fiordispino.GamesToPlay', owner=user, game=games[0])

        path = reverse('games-to-play-detail', kwargs={'pk': my_entry.id})
        client = get_client(user=user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify that it is no longer in the database
        assert GamesToPlay.objects.filter(pk=my_entry.id).exists() is False

    def test_owner_can_update(self, user, games):
        """Test that the owner can update an entry in their backlog."""
        my_entry = mixer.blend('fiordispino.GamesToPlay', owner=user, game=games[0])

        path = reverse('games-to-play-detail', kwargs={'pk': my_entry.id})
        client = get_client(user=user)

        update_data = {'game': games[0].id}

        response = client.put(path, update_data)
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_see(self, user):
        """Test that an authenticated user can view the list of games to play."""
        path = reverse('games-to-play-list')
        client = get_client(user=user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    # --- STRANGER TESTS (Read Only, No Write) ---

    def test_stranger_can_see_others_games(self, games_to_play, user):
        """Test that a user can see another user's backlog."""
        target_entry = games_to_play[0]

        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})
        client = get_client(user=user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_stranger_cant_delete_others_games(self, games_to_play, user):
        """Test that a stranger cannot delete another user's backlog entry."""
        target_entry = games_to_play[0]

        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})
        client = get_client(user=user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_stranger_cant_update_others_games(self, games_to_play, games, user):
        """Test that a stranger cannot update another user's backlog entry."""
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        client = get_client(user=user)
        data = {'game': games[0].id}

        response = client.put(path, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ADMIN TESTS (Now with Delete/Update access) ---

    def test_admin_can_see(self, admin_user):
        """Test that an admin can view the backlog list."""
        path = reverse('games-to-play-list')
        admin = get_admin(admin_user)

        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_delete_user_games(self, admin_user, games_to_play):
        """
        UPDATED: Test that an admin is now allowed to delete any user's backlog entry.
        """
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)

        response = admin.delete(path)

        # Expected status changed from 403 to 204
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert GamesToPlay.objects.filter(pk=target_entry.id).exists() is False

    def test_admin_can_update_user_games(self, admin_user, games_to_play, games):
        """
        UPDATED: Test that an admin is now allowed to update any user's backlog entry.
        """
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)
        data = {'game': games[0].id}

        response = admin.put(path, data)

        # Expected status changed from 403 to 200
        assert response.status_code == status.HTTP_200_OK

    # --- ANONYMOUS TESTS (No Access) ---

    def test_anonymous_user_cannot_see_games(self, games_to_play):
        """Test that unauthenticated users are denied access."""
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        client = get_client()  # Anonymous

        response = client.get(path)
        # Fails IsAuthenticated check -> 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
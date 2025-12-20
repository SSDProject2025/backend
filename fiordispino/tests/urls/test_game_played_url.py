from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model
from fiordispino.models import GamePlayed
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGamePlayedUrl:

    # --- OWNER TESTS (Full Access: Create, Read, Update, Delete) ---

    def test_owner_can_add(self, user, games):
        """Test that the owner of the library can add a new played game."""
        path = reverse('games-played-list')
        client = get_client(user)
        data = {'game': games[0].id, 'rating': 9}

        response = client.post(path, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['owner'] == user.id
        assert response.data['rating'] == 9

    def test_owner_can_delete(self, user, games):
        """Test that the owner can delete their own entries."""
        my_entry = mixer.blend('fiordispino.GamePlayed', owner=user, game=games[0], rating=8)

        path = reverse('games-played-detail', kwargs={'pk': my_entry.id})
        client = get_client(user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert GamePlayed.objects.filter(pk=my_entry.id).exists() is False

    def test_owner_can_update(self, user, games):
        """Test that the owner can update the rating of their entries."""
        my_entry = mixer.blend('fiordispino.GamePlayed', owner=user, game=games[0], rating=5)

        path = reverse('games-played-detail', kwargs={'pk': my_entry.id})
        client = get_client(user)
        update_data = {'game': games[0].id, 'rating': 10}

        response = client.put(path, update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rating'] == 10

    # --- AUTHENTICATED STRANGER TESTS (Read Only) ---

    def test_auth_stranger_can_see_others_games(self, games):
        """Test that a logged-in user can view entries belonging to others."""
        owner = mixer.blend(get_user_model())
        stranger = mixer.blend(get_user_model())

        target_entry = mixer.blend('fiordispino.GamePlayed', owner=owner, game=games[0], rating=5)

        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})
        client = get_client(stranger)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_auth_stranger_cant_delete_others_games(self, games, user):
        """Test that a non-admin stranger cannot delete someone else's entry."""
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])

        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})
        client = get_client(user=user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ANONYMOUS TESTS (No Access) ---

    def test_anonymous_user_cannot_see_games(self, games):
        """Test that unauthenticated users cannot access detail views."""
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        client = get_client()

        response = client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # --- ADMIN TESTS (Elevated Access) ---

    def test_admin_can_see(self, admin_user):
        """Test that an admin can list all played games."""
        path = reverse('games-played-list')
        admin = get_admin(admin_user)

        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_delete_user_games(self, admin_user, games):
        """
        UPDATED: Test that an admin is now allowed to delete any user's game entry.
        We force a valid Decimal value for the game to prevent SQLite conversion errors.
        """
        game = games[0]
        # Force safe values before starting the test logic
        game.global_rating = Decimal('0.00')
        game.rating_count = 0
        game.save()

        target_entry = mixer.blend('fiordispino.GamePlayed', game=game, rating=10)
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)
        response = admin.delete(path)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert GamePlayed.objects.filter(pk=target_entry.id).exists() is False

        # Verify the signal recalculated correctly
        game.refresh_from_db()
        assert game.rating_count == 0

    def test_admin_can_update_user_games(self, admin_user, games):
        """
        UPDATED: Test that an admin is now allowed to update any user's game entry.
        """
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0], rating=1)
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)
        data = {'game': games[0].id, 'rating': 10}

        response = admin.put(path, data)

        # Expected status changed from 403 to 200
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rating'] == 10
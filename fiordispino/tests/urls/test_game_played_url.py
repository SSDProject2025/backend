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
        path = reverse('games-played-list')
        client = get_client(user)
        data = {'game': games[0].id, 'rating': 9}

        response = client.post(path, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['owner'] == user.id
        assert response.data['rating'] == 9

    def test_owner_can_delete(self, user, games):
        my_entry = mixer.blend('fiordispino.GamePlayed', owner=user, game=games[0], rating=8)

        path = reverse('games-played-detail', kwargs={'pk': my_entry.id})
        client = get_client(user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert GamePlayed.objects.filter(pk=my_entry.id).exists() is False

    def test_owner_can_update(self, user, games):
        my_entry = mixer.blend('fiordispino.GamePlayed', owner=user, game=games[0], rating=5)

        path = reverse('games-played-detail', kwargs={'pk': my_entry.id})
        client = get_client(user)
        update_data = {'game': games[0].id, 'rating': 10}

        response = client.put(path, update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rating'] == 10

    def test_user_can_see_own_games(self, user):
        path = reverse('games-played-list')
        client = get_client(user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    # --- AUTHENTICATED STRANGER TESTS (Read Only) ---

    def test_auth_stranger_can_see_others_games(self, games):
        owner = mixer.blend(get_user_model())
        stranger = mixer.blend(get_user_model())

        target_entry = mixer.blend('fiordispino.GamePlayed', owner=owner, game=games[0], rating=5)

        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        client = get_client(stranger)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_auth_stranger_cant_delete_others_games(self, games, user):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])

        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})
        client = get_client(user=user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_stranger_cant_update_others_games(self, games, user):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        client = get_client(user=user)
        data = {'game': games[0].id, 'rating': 10}

        response = client.put(path, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ANONYMOUS TESTS (No Access) ---

    def test_anonymous_user_cannot_see_games(self, games):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        client = get_client()

        response = client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # --- ADMIN TESTS ---

    def test_admin_can_see(self, admin_user):
        path = reverse('games-played-list')
        admin = get_admin(admin_user)

        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_admin_cant_delete_user_games(self, admin_user, games):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)

        response = admin.delete(path)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_cant_update_user_games(self, admin_user, games):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)
        data = {'game': games[0].id, 'rating': 10}

        response = admin.put(path, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
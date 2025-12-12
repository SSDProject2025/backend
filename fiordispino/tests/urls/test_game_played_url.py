import pytest
from django.urls import reverse
from rest_framework import status
from mixer.backend.django import mixer
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

    def test_user_can_see(self, user):
        path = reverse('games-played-list')
        client = get_client(user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    # --- STRANGER TESTS (Read Only) ---

    def test_stranger_can_see_others_games(self, games):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])

        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})
        client = get_client() # Unauthenticated / Stranger

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_stranger_cant_delete_others_games(self, games):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])

        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})
        client = get_client()

        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_stranger_cant_update_others_games(self, games):
        target_entry = mixer.blend('fiordispino.GamePlayed', game=games[0])
        path = reverse('games-played-detail', kwargs={'pk': target_entry.id})

        client = get_client()
        data = {'game': games[0].id, 'rating': 10}

        response = client.put(path, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ADMIN TESTS (Read Only constraint) ---

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
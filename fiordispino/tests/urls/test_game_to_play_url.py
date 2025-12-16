import pytest
from django.urls import reverse
from rest_framework import status
from mixer.backend.django import mixer
from fiordispino.models import GamesToPlay
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGameToPlayUrl:

    # --- OWNER TESTS (Full Access: Create, Read, Update, Delete) ---

    def test_owner_can_add(self, user,games_to_play_data):
        path = reverse('games-to-play-list')
        client = get_client(user=user)

        response = client.post(path, games_to_play_data)

        assert response.status_code == status.HTTP_201_CREATED

        # verify that the owner is the one who created the entry
        assert response.data['owner'] == user.id

    def test_owner_can_delete(self, user, games):
        # create a fake db entry, then delete it

        my_entry = mixer.blend('fiordispino.GamesToPlay', owner=user, game=games[0])

        path = reverse('games-to-play-detail', kwargs={'pk': my_entry.id})
        client = get_client(user=user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # verify that it is not in the db anymore
        assert GamesToPlay.objects.filter(pk=my_entry.id).exists() is False

    def test_owner_can_update(self, user, games):
        my_entry = mixer.blend('fiordispino.GamesToPlay', owner=user, game=games[0])

        path = reverse('games-to-play-detail', kwargs={'pk': my_entry.id})
        client = get_client(user=user)

        update_data = {'game': games[0].id}

        response = client.put(path, update_data)
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_see(self, user):
        path = reverse('games-to-play-list')
        client = get_client(user=user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    # --- STRANGER TESTS (Read Only, No Write) ---

    def test_stranger_can_see_others_games(self, games_to_play, user):
        target_entry = games_to_play[0]

        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})
        client = get_client(user=user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_stranger_cant_delete_others_games(self, games_to_play, user):
        target_entry = games_to_play[0]  # the fixture create entries with random owners

        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})
        client = get_client(user=user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_stranger_cant_update_others_games(self, games_to_play, games, user):
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        client = get_client(user=user)  # Stranger
        data = {'game': games[0].id}

        response = client.put(path, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ADMIN TESTS (Read Only constraint) ---

    def test_admin_can_see(self, admin_user):
        path = reverse('games-to-play-list')
        admin = get_admin(admin_user)

        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK

    def test_admin_cant_delete_user_games(self, admin_user, games_to_play):
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)

        response = admin.delete(path)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_cant_update_user_games(self, admin_user, games_to_play, games):
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        admin = get_admin(admin_user)
        data = {'game': games[0].id}

        response = admin.put(path, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ANONYMOUS TESTS (No Access) ---

    def test_anonymous_user_cannot_see_games(self, games_to_play):
        target_entry = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_entry.id})

        client = get_client()  # No user = Anonymous

        response = client.get(path)
        # Fails IsAuthenticated check -> 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
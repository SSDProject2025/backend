import pytest
from django.contrib.auth.models import User
from fiordispino.models import Game, GamesToPlay
from mixer.backend.django import mixer
import pytest
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rest_framework import status
from mixer.backend.django import mixer
from fiordispino.models import Game
from fiordispino.tests.utils_testing import *

@pytest.mark.django_db
class TestGamesToPlay:

    def test_owner_can_edit(self, games_to_play, games_to_play_data):
        target_obj = games_to_play[0]
        owner = target_obj.owner
        path = reverse('games-to-play-detail', kwargs={'pk': target_obj.id})
        client = get_client()
        client.force_authenticate(user=owner)
        response = client.put(path, games_to_play_data, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_owner_cannot_delete(self, games_to_play):
        target_obj = games_to_play[0]
        owner = target_obj.owner
        path = reverse('games-to-play-detail', kwargs={'pk': target_obj.id})
        client = get_client()
        client.force_authenticate(user=owner)
        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_create(self, games_to_play_data):
        path = reverse('games-to-play-list')
        client = get_client()
        response = client.post(path, games_to_play_data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_user_can_see(self):
       path = reverse('games-to-play-list')
       client = get_client()
       response = client.get(path)
       assert response.status_code == status.HTTP_200_OK
       obj = parse(response)
       assert obj is not None

    def test_admin_cannot_edit(self, games_to_play_data, games_to_play, admin_user):
        target_obj = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_obj.id})
        client = get_admin(admin_user)
        response = client.put(path, games_to_play_data, format='json')

    def test_admin_cannot_delete(self, games_to_play_data, games_to_play, admin_user):
        target_obj = games_to_play[0]
        path = reverse('games-to-play-detail', kwargs={'pk': target_obj.id})
        client = get_admin(admin_user)
        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_cannot_create(self, games_to_play_data, games_to_play, admin_user):
        target_obj = games_to_play[0]
        path = reverse('games-to-play-list')
        client = get_admin(admin_user)
        response = client.post(path, games_to_play_data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
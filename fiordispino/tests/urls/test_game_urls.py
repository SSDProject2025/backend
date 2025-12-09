import pytest
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rest_framework import status
from mixer.backend.django import mixer
from fiordispino.models import Game


@pytest.mark.django_db
class TestGameUrl:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def game(self):
        # Creates a single Game instance with random data
        return mixer.blend(Game, title="Test Game")

    def test_game_list_url_resolves(self):
        # The router creates 'game-list' automatically
        path = reverse('game-list')

        # Assert that the path is resolved correctly to the viewset
        assert resolve(path).view_name == 'game-list'

    def test_game_detail_url_resolves(self, game):
        # The router creates 'game-detail' taking a pk
        path = reverse('game-detail', kwargs={'pk': game.pk})

        assert resolve(path).view_name == 'game-detail'

    def test_get_game_list(self, client):
        # Create dummy data. Mixer automatically fills required fields
        # (title, pegi, etc.) with random valid data. I hardcode the name to respect length limits
        mixer.blend(Game, title="Super Mario")
        mixer.blend(Game, title="Sonic")
        mixer.blend(Game, title="Tetris")

        path = reverse('game-list')
        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    def test_get_game_detail(self, client, game):
        # Get a specific game via primary key
        path = reverse('game-detail', kwargs={'pk': game.pk})
        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK

        # Verify the data returned matches the fixture
        # (Assuming your GameSerializer returns the title field)
        assert response.json()['title'] == game.title
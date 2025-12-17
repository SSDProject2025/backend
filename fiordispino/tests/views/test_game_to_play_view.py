import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from fiordispino.models import GamesToPlay, GamePlayed
from fiordispino.tests.utils_testing import *
from fiordispino.core.exceptions import GameAlreadyInGamesPlayed


@pytest.mark.django_db
class TestGamesToPlayView:

    def test_move_to_played_should_fail_if_game_does_not_exist(self, user, games):
        """
        if the user tries to add a game to the games played list which does not exist it should throw a 404 not found error
        """
        game = games[0]
        client = get_client(user)
        url = reverse('games-to-play-move-to-played', kwargs={'pk': game.pk})
        payload = {'rating': 9}
        response = client.post(url, payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_move_to_played_success(self, user, games):
        """
        Verify 'move_to_played' action works correctly:
        - Creates GamePlayed entry
        - Deletes GamesToPlay entry
        """
        game = games[0]
        entry_to_play = GamesToPlay.objects.create(owner=user, game=game)

        client = get_client(user)

        url = reverse('games-to-play-move-to-played', kwargs={'pk': entry_to_play.pk})
        payload = {'rating': 9}

        response = client.post(url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert not GamesToPlay.objects.filter(pk=entry_to_play.pk).exists()

        played_entry = GamePlayed.objects.get(owner=user, game=game)
        assert played_entry.rating == 9

    def test_move_to_played_missing_rating(self, user, games):
        game = games[0]
        entry_to_play = GamesToPlay.objects.create(owner=user, game=game)

        client = get_client(user)
        url = reverse('games-to-play-move-to-played', kwargs={'pk': entry_to_play.pk})

        response = client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = parse(response)
        assert 'detail' in data
        assert GamesToPlay.objects.filter(pk=entry_to_play.pk).exists()

    def test_move_to_played_permission_denied(self, user, games):
        """
        Verify that a user cannot move another user's game.
        """
        attacker = mixer.blend(get_user_model())
        game = games[0]
        entry_to_play = GamesToPlay.objects.create(owner=user, game=game)

        client = get_client(attacker)

        url = reverse('games-to-play-move-to-played', kwargs={'pk': entry_to_play.pk})

        response = client.post(url, {'rating': 10})

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_create_duplicate_in_other_table_fails(self, user, games, games_to_play_data):
        """
        Verify validation: cannot add to 'GamesToPlay' if already in 'GamePlayed'.
        Uses 'games_to_play_data' fixture for payload.
        """
        game = games[0]
        GamePlayed.objects.create(owner=user, game=game, rating=8)

        client = get_client(user)
        url = reverse('games-to-play-list')

        response = client.post(url, games_to_play_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = parse(response)
        assert GameAlreadyInGamesPlayed.default_detail in str(data)

    
    def test_get_by_owner_should_fail_with_invalid_username(self, user):

        evil_username = "' OR '1'='1'" # classic sql injection code
        url = reverse('games-to-play-get-by-owner', kwargs={'username': evil_username})
        client = get_client(user)
        response = client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_by_owner_success(self, user, games):
        GamesToPlay.objects.create(owner=user, game=games[0])

        client = get_client(user)
        url = reverse('games-to-play-get-by-owner', kwargs={'username': user.username})

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = parse(response)

        assert len(data) == 1

    def test_get_by_owner_with_empty_list(self, user):
        client = get_client(user)
        url = reverse('games-to-play-get-by-owner', kwargs={'username': user.username})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = parse(response)
        assert len(data) == 0

    def test_create_duplicate_in_same_table_fails(self, user, games):
        game = games[0]
        # 1. Create the entry first manually
        GamesToPlay.objects.create(owner=user, game=game)

        client = get_client(user)
        url = reverse('games-to-play-list')

        # 2. Try to add the same game again via API
        payload = {'game': game.id}
        response = client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_move_to_played_fails_if_destination_exists(self, user, games):
        game = games[0]

        # Setup: The game is in "To Play" AND already in "Played"
        entry_to_play = GamesToPlay.objects.create(owner=user, game=game)
        GamePlayed.objects.create(owner=user, game=game, rating=10)

        client = get_client(user)
        url = reverse('games-to-play-move-to-played', kwargs={'pk': entry_to_play.pk})
        payload = {'rating': 9}

        # Action: Try to move it
        response = client.post(url, payload)

        # Expectation: 400 Bad Request (not 500 IntegrityError)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Ensure the original 'To Play' entry was NOT deleted because the move failed
        assert GamesToPlay.objects.filter(pk=entry_to_play.pk).exists()


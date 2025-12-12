import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from fiordispino.models import GamesToPlay, GamePlayed
from fiordispino.tests.utils_testing import *
from fiordispino.core.exceptions import GameAlreadyInGamesToPlay


@pytest.mark.django_db
class TestGamePlayedView:

    def test_move_to_backlog_should_fail_if_game_does_not_exist(self, user, games):
        """
        If the user tries to move a game that doesn't exist in 'GamePlayed', return 404.
        """
        game = games[0]
        client = get_client(user)
        url = reverse('games-played-move-to-backlog', kwargs={'pk': game.pk})

        response = client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_move_to_backlog_success(self, user, games):
        """
        Verify 'move_to_backlog' action:
        - Creates GamesToPlay entry
        - Deletes GamePlayed entry
        - Rating is discarded (as GamesToPlay has no rating)
        """
        game = games[0]
        played_entry = GamePlayed.objects.create(owner=user, game=game, rating=9)

        client = get_client(user)
        url = reverse('games-played-move-to-backlog', kwargs={'pk': played_entry.pk})

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert not GamePlayed.objects.filter(pk=played_entry.pk).exists()
        assert GamesToPlay.objects.filter(owner=user, game=game).exists()

    def test_move_to_backlog_permission_denied(self, user, games):
        """
        Verify that a user cannot move another user's game.
        """
        attacker = mixer.blend(User)
        game = games[0]
        played_entry = GamePlayed.objects.create(owner=user, game=game, rating=8)

        client = get_client(attacker)
        url = reverse('games-played-move-to-backlog', kwargs={'pk': played_entry.pk})

        response = client.post(url)

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_create_duplicate_in_other_table_fails(self, user, games):
        """
        Verify validation: cannot add to 'GamePlayed' (via standard Create)
        if it already exists in 'GamesToPlay'.
        """
        game = games[0]

        GamesToPlay.objects.create(owner=user, game=game)

        client = get_client(user)
        url = reverse('games-played-list')
        payload = {'game': game.pk, 'rating': 10}
        response = client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = parse(response)
        assert GameAlreadyInGamesToPlay.default_detail in str(data)
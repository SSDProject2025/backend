import pytest
from django.contrib.auth.models import User
from fiordispino.models import Game, GamesToPlay
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestGamesToPlay:

    @pytest.fixture
    def user(self):
        return mixer.blend(User)

    @pytest.fixture
    def game(self):
        return mixer.blend(Game, title="GTA VI")

    @pytest.fixture
    def gamesToPlay(self, user, game):
        entry = mixer.blend(GamesToPlay, owner=user)
        entry.games.add(game)
        return entry

    def test_add_game(self, user, game):
        entry = GamesToPlay.objects.create(owner=user)

        assert entry.games.count() == 0

        entry.games.add(game)

        assert entry.games.count() == 1
        assert entry.games.first() == game
        assert entry.owner == user

    def test_remove_game(self, gamesToPlay, game):
        assert gamesToPlay.games.count() == 1

        gamesToPlay.games.remove(game)

        assert GamesToPlay.objects.count() == 1
        assert gamesToPlay.games.count() == 0
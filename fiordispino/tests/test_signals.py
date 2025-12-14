import pytest
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model
from fiordispino.models import Game, GamePlayed
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
def test_signal_rating_creation(user, games):
    # when a user rates a game, the game's global rating should change accordingly
    game = games[0]

    assert game.global_rating == 0.0
    assert game.rating_count == 0

    GamePlayed.objects.create(owner=user, game=game, rating=8)

    game.refresh_from_db()

    assert game.rating_count == 1
    assert game.global_rating == 8.0


@pytest.mark.django_db
def test_signal_rating_average_calculation(user, games):
    # the global rating should be an avg of all the ratings
    game = games[1]

    user2 = mixer.blend(get_user_model())

    # add 2 ratings of the same game by two different users
    # user -> rating = 10
    # user2 -> rating = 6
    # global_rating = (10+6)/2 = 8.0 -> because it's a float value
    GamePlayed.objects.create(owner=user, game=game, rating=10)
    GamePlayed.objects.create(owner=user2, game=game, rating=6)

    game.refresh_from_db()

    assert game.rating_count == 2
    assert game.global_rating == 8.0


@pytest.mark.django_db
def test_signal_rating_update(user, games):
    # if a user updates a rating, the global average should change accordingly
    game = games[0]
    User = get_user_model()
    user2 = mixer.blend(User)

    # two ratings -> 10 and 10, average should be 10
    gp1 = GamePlayed.objects.create(owner=user, game=game, rating=10)
    GamePlayed.objects.create(owner=user2, game=game, rating=10)

    game.refresh_from_db()
    assert game.global_rating == 10.0

    # a user changes their rating from 10 to 2 -> (10+2)/2=6.0
    gp1.rating = 2
    gp1.save()

    game.refresh_from_db()

    assert game.global_rating == 6.0
    assert game.rating_count == 2


@pytest.mark.django_db
def test_signal_rating_deletion(user, games):
    # if user deletes their rating the global rating should change accordignly or drop to 0 if it was the only rating for the game
    game = games[2]

    gp = GamePlayed.objects.create(owner=user, game=game, rating=9)

    game.refresh_from_db()
    assert game.rating_count == 1
    assert game.global_rating == 9.0

    gp.delete()

    game.refresh_from_db()

    assert game.rating_count == 0
    assert game.global_rating == 0.0


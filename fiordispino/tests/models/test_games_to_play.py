import time

from django.contrib.auth import get_user_model
from django.db import IntegrityError

from fiordispino.models import GamesToPlay
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGamesToPlay:

    def test_str_representation(self, user, games):
        game = games[0]
        entry = GamesToPlay.objects.create(owner=user, game=game)

        expected_str = f"{user.username} wants to play {game.title}"
        assert str(entry) == expected_str

    def test_uniqueness_constraint(self, user, games):
        game = games[0]

        GamesToPlay.objects.create(owner=user, game=game)

        with pytest.raises(IntegrityError):
            GamesToPlay.objects.create(owner=user, game=game)

    def test_different_users_can_add_same_game(self, games):
        user1 = mixer.blend(get_user_model())
        user2 = mixer.blend(get_user_model())
        game = games[0]

        entry1 = GamesToPlay.objects.create(owner=user1, game=game)

        entry2 = GamesToPlay.objects.create(owner=user2, game=game)

        assert entry1.pk != entry2.pk
        assert GamesToPlay.objects.count() == 2

    def test_timestamps_logic(self, user, games):
        entry = GamesToPlay.objects.create(owner=user, game=games[0])

        original_created_at = entry.created_at
        original_updated_at = entry.updated_at

        assert original_created_at is not None
        assert original_updated_at is not None

        # Facciamo passare un istante per garantire che il tempo cambi
        time.sleep(0.01)

        # Modifichiamo l'oggetto (anche un save a vuoto triggera auto_now)
        entry.save()

        # Ricarichiamo dal DB per essere sicuri dei dati
        entry.refresh_from_db()

        # created_at DEVE rimanere uguale
        assert entry.created_at == original_created_at

        # updated_at DEVE essere maggiore del precedente
        assert entry.updated_at > original_updated_at

    def test_cascade_delete_game(self, user, games):
        game = games[0]
        GamesToPlay.objects.create(owner=user, game=game)

        assert GamesToPlay.objects.count() == 1

        # Cancello il gioco originale
        game.delete()

        # La relazione deve essere sparita (on_delete=models.CASCADE)
        assert GamesToPlay.objects.count() == 0

    def test_cascade_delete_user(self, user, games):
        GamesToPlay.objects.create(owner=user, game=games[0])

        assert GamesToPlay.objects.count() == 1

        # Cancello l'utente
        user.delete()

        # La lista deve essere sparita
        assert GamesToPlay.objects.count() == 0
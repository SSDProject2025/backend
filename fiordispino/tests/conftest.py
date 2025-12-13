import pytest
import pytest
from django.conf import settings
from rest_framework.test import APIClient
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model


@pytest.fixture(autouse=True)
def use_tmp_media_root(tmp_path, settings):
    """
    this ficture is automatically called in every test
    set MEDIA_ROOT = tmp_path destroyed at the end of every test
    """
    settings.MEDIA_ROOT = tmp_path / "media"

    @pytest.fixture(autouse=True)
    def use_tmp_media_root(tmp_path, settings):
        """
        Sets MEDIA_ROOT = tmp_path destroyed at the end of every test
        """
        settings.MEDIA_ROOT = tmp_path / "media"
        yield

    @pytest.fixture
    def api_client():
        """
        Restituisce un client API per fare richieste nei test
        """
        return APIClient()

    @pytest.fixture
    def user(db):
        """
        Crea un utente standard usando il Modello Custom.
        Usa 'mixer' per popolarlo con dati casuali ma validi.
        """
        return mixer.blend(get_user_model())

    @pytest.fixture
    def admin_user(db):
        """
        Crea un superuser/admin.
        """
        return mixer.blend(get_user_model(), is_superuser=True, is_staff=True)

    @pytest.fixture
    def auth_client(api_client, user):
        """
        Restituisce un client API che è già loggato come utente standard.
        """
        api_client.force_authenticate(user=user)
        return api_client

    # run tests
    yield
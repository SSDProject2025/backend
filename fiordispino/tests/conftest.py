import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture(autouse=True)
def use_tmp_media_root(tmp_path, settings):
    """
    This fixture is automatically called in every test.
    Sets MEDIA_ROOT = tmp_path, destroyed at the end of every test.
    """
    settings.MEDIA_ROOT = tmp_path / "media"

@pytest.fixture
def api_client():
    """
    Restituisce un client API (DRF) per fare richieste nei test.
    """
    return APIClient()

@pytest.fixture
def user(db):
    """
    Crea un utente standard nel database di test e lo restituisce.
    Usa create_user per garantire che la password sia hashata correttamente
    e che i campi (email, username) siano popolati secondo il tuo modello custom.
    """
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="strong_password_123"
    )
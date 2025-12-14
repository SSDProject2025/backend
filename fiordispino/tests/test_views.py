import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:
    # Sostituisci 'register' con il nome reale del tuo URL pattern se diverso
    # Oppure usa l'url diretto: url = "/api/v1/auth/registration/"
    try:
        url = reverse('register')
    except:
        url = "/api/v1/auth/registration/"

    def test_register_success(self, api_client):
        """
        Verifica che la registrazione funzioni correttamente con dati validi.
        Testa anche la logica della View che converte 'password1' in 'password'.
        """
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "StrongPass123!",  # La view si aspetta password1 o password
            "password2": "StrongPass123!"
        }

        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'key' in response.data

        # Verifica che l'utente sia nel DB
        user = User.objects.get(email="new@example.com")
        assert user.username == "newuser"
        # Verifica che il token sia stato creato
        assert Token.objects.filter(user=user).exists()

    def test_register_passwords_mismatch(self, api_client):
        """
        Verifica che restituisca 400 se le password non coincidono.
        """
        payload = {
            "username": "failuser",
            "email": "fail@example.com",
            "password1": "PassA",
            "password2": "PassB"
        }

        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_email_already_exists(self, api_client, user):
        """
        Verifica che non si possa registrare un'email già esistente.
        (Usa la fixture 'user' che ha già creato un utente nel DB)
        """
        payload = {
            "username": "anotheruser",
            "email": user.email,  # Usiamo l'email dell'utente già esistente
            "password1": "StrongPass123!",
            "password2": "StrongPass123!"
        }

        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_invalid_data_format(self, api_client):
        """
        Verifica il comportamento con campi mancanti.
        """
        payload = {
            "email": "incomplete@example.com"
            # Manca username e password
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginView:

    try:
        url = reverse('login')
    except:
        url = "/api/v1/auth/login/"

    def test_login_success(self, api_client, user):
        """
        Verifica il login con credenziali corrette (Email + Password).
        Nota: La fixture 'user' in conftest.py deve creare l'utente con password nota.
        """
        # Assumiamo che la fixture 'user' abbia password='strong_password_123'
        # (come definito nel tuo conftest.py)
        payload = {
            "email": user.email,
            "password": "strong_password_123"
        }

        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert 'key' in response.data

        token = Token.objects.get(user=user)
        assert response.data['key'] == token.key

    def test_login_invalid_password(self, api_client, user):
        """
        Verifica che il login fallisca con password errata (401).
        """
        payload = {
            "email": user.email,
            "password": "wrong_password"
        }

        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == 'Invalid credentials'

    def test_login_non_existent_email(self, api_client):
        """
        Verifica che il login fallisca se l'email non esiste (401).
        """
        payload = {
            "email": "ghost@example.com", # Email valida come formato
            "password": "any_password"
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == 'Invalid credentials'

    def test_login_missing_fields(self, api_client):
        """
        Verifica che la view restituisca 400 se mancano email o password.
        Ora usiamo il serializer, quindi ci aspettiamo errori strutturati per campo.
        """
        # Caso 1: Manca password
        response = api_client.post(self.url, {"email": "test@test.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # DRF restituisce un dizionario: {'password': ['This field is required.']}
        assert 'password' in response.data

        # Caso 2: Manca email
        response = api_client.post(self.url, {"password": "pwd"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
import pytest
from django.contrib.auth import get_user_model
from fiordispino.authentication import EmailBackend

User = get_user_model()


@pytest.mark.django_db
class TestEmailBackend:

    def test_authenticate_success(self, user):
        """
        Verifica che l'autenticazione funzioni correttamente quando
        email e password sono validi.
        """

        # Impostiamo una password nota per il test
        password = "strong_password_123"
        user.set_password(password)
        user.save()

        backend = EmailBackend()

        # Testiamo passando l'email esplicitamente come kwargs
        authenticated_user = backend.authenticate(
            request=None,
            email=user.email,
            password=password
        )

        assert authenticated_user is not None
        assert authenticated_user == user

    def test_authenticate_wrong_password(self, user):
        """
        Verifica che l'autenticazione fallisca (ritorni None)
        se la password è errata.
        """
        user.set_password("correct_password")
        user.save()

        backend = EmailBackend()

        authenticated_user = backend.authenticate(
            request=None,
            email=user.email,
            password="wrong_password"
        )

        assert authenticated_user is None

    def test_authenticate_user_does_not_exist(self):
        """
        Verifica che l'autenticazione fallisca se l'email non esiste nel DB.
        """
        backend = EmailBackend()

        authenticated_user = backend.authenticate(
            request=None,
            email="non_existent@example.com",
            password="any_password"
        )

        assert authenticated_user is None

    def test_authenticate_using_username_argument(self, user):
        """
        Verifica che il backend accetti l'email anche se passata
        nel parametro posizionale 'username'.
        (Django passa 'username' di default anche se il campo è un'email).
        """
        password = "password123"
        user.set_password(password)
        user.save()

        backend = EmailBackend()

        # Qui passiamo l'email all'interno dell'argomento 'username'
        authenticated_user = backend.authenticate(
            request=None,
            username=user.email,
            password=password
        )

        assert authenticated_user == user

    def test_authenticate_missing_credentials(self):
        """
        Verifica che il metodo ritorni None se email o password sono None.
        """
        backend = EmailBackend()

        # Caso 1: Email mancante
        assert backend.authenticate(request=None, email=None, password="pwd") is None

        # Caso 2: Password mancante
        assert backend.authenticate(request=None, email="test@test.com", password=None) is None

    def test_authenticate_inactive_user_behavior(self, user):
        """
        NOTA: Questo test verifica il comportamento attuale del tuo codice.
        Attualmente, il tuo codice PERMETTE il login anche se is_active=False.
        """
        password = "password"
        user.set_password(password)
        user.is_active = False  # Disattiviamo l'utente
        user.save()

        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            email=user.email,
            password=password
        )

        # Se vuoi che gli utenti bannati possano loggarsi, questo assert deve essere True.
        # Se invece vuoi bloccarli, dovrai modificare la classe EmailBackend.
        assert authenticated_user == user
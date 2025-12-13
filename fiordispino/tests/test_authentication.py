import pytest
from django.contrib.auth import get_user_model
from fiordispino.authentication import EmailBackend

User = get_user_model()


@pytest.mark.django_db
class TestEmailBackend:

    def test_authenticate_success(self, user):
        """
        Verifica che l'autenticazione funzioni con email e password corretti.
        """
        # Impostiamo una password nota per il test
        password = "strong_password_123"
        user.set_password(password)
        user.save()

        backend = EmailBackend()

        # Simuliamo la chiamata di authenticate
        authenticated_user = backend.authenticate(request=None, email=user.email, password=password)

        assert authenticated_user is not None
        assert authenticated_user == user

    def test_authenticate_wrong_password(self, user):
        """
        Verifica che l'autenticazione fallisca se la password è errata.
        """
        user.set_password("correct_password")
        user.save()

        backend = EmailBackend()

        authenticated_user = backend.authenticate(request=None, email=user.email, password="wrong_password")

        assert authenticated_user is None

    def test_authenticate_user_does_not_exist(self):
        """
        Verifica che l'autenticazione fallisca se l'email non esiste nel DB.
        """
        backend = EmailBackend()

        authenticated_user = backend.authenticate(request=None, email="ghost@example.com", password="any_password")

        assert authenticated_user is None

    def test_authenticate_using_username_argument(self, user):
        """
        Verifica che il backend accetti l'email anche se passata nel parametro 'username'.
        (Molti form di Django passano 'username' anche se il campo è un'email).
        """
        password = "password123"
        user.set_password(password)
        user.save()

        backend = EmailBackend()

        # Qui passiamo l'email all'interno dell'argomento 'username'
        authenticated_user = backend.authenticate(request=None, username=user.email, password=password)

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

    def test_authenticate_inactive_user(self, user):
        """
        Opzionale: Verifica il comportamento con utenti inattivi.
        Nota: Il tuo codice attuale NON controlla se l'utente è attivo (is_active).
        Se volessi impedire il login agli utenti bannati, dovresti modificare il backend.
        """
        user.set_password("password")
        user.is_active = False  # Utente disattivato
        user.save()

        backend = EmailBackend()
        authenticated_user = backend.authenticate(request=None, email=user.email, password="password")

        # Al momento il tuo codice permette il login anche se is_active=False.
        # Se questo è il comportamento voluto, il test deve aspettarsi 'user'.
        # Se invece vuoi bloccarli, il test dovrebbe aspettarsi None.
        assert authenticated_user == user
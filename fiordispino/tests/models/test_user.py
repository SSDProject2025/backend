import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

# Recuperiamo il modello User attivo
User = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_user_string_representation(self):
        """
        Verifica che il metodo __str__ restituisca l'email.
        """
        email = "test@example.com"
        user = User.objects.create_user(email=email, password="password")
        assert str(user) == email

    def test_email_field_is_unique(self):
        """
        Verifica che non sia possibile creare due utenti con la stessa email.
        Deve sollevare un IntegrityError (vincolo database).
        """
        email = "unique@example.com"
        User.objects.create_user(email=email, password="password")

        with pytest.raises(IntegrityError):
            User.objects.create_user(email=email, password="password2")

    def test_username_is_not_unique(self):
        """
        CRITICO: Verifica che sia possibile creare due utenti con lo STESSO username.
        Il tuo modello ha unique=False su username, quindi questo test DEVE passare.
        """
        username = "mario_rossi"

        # Utente 1
        user1 = User.objects.create_user(
            email="mario1@example.com",
            password="pwd",
            username=username
        )

        # Utente 2 (Stesso username, email diversa)
        user2 = User.objects.create_user(
            email="mario2@example.com",
            password="pwd",
            username=username
        )

        assert user1.username == user2.username
        assert user1.pk != user2.pk
        assert User.objects.filter(username=username).count() == 2

    def test_username_can_be_null(self):
        """
        Verifica che lo username possa essere None o vuoto (blank=True, null=True).
        """
        user = User.objects.create_user(
            email="nousername@example.com",
            password="pwd",
            username=None
        )
        assert user.username is None

    def test_username_field_config(self):
        """
        Verifica la configurazione dei campi speciali di autenticazione.
        """
        assert User.USERNAME_FIELD == 'email'
        assert 'username' in User.REQUIRED_FIELDS
        # REQUIRED_FIELDS non deve contenere USERNAME_FIELD
        assert 'email' not in User.REQUIRED_FIELDS

    def test_user_has_correct_app_label(self):
        """
        Opzionale: verifica che l'app_label sia impostata correttamente nei Meta.
        """
        assert User._meta.app_label == 'fiordispino'
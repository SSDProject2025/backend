import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestCustomUserManager:

    def test_create_user_success(self):
        """
        Verifica la creazione di un utente normale con email, username e password.
        """
        email = "normal@user.com"
        password = "foo_password"
        username = "normaluser"

        user = User.objects.create_user(email=email, password=password, username=username)

        assert user.email == email
        assert user.username == username
        assert user.check_password(password) is True
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_email_normalization(self):
        """
        Verifica che l'email venga normalizzata (il dominio diventa minuscolo).
        """
        email = "test@EXAMPLE.com"
        user = User.objects.create_user(email=email, password="password", username="test")

        # BaseUserManager.normalize_email trasforma il dominio in lowercase
        assert user.email == "test@example.com"

    def test_create_user_missing_email(self):
        """
        Verifica che venga sollevato un ValueError se l'email è mancante o vuota.
        """
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(email="", password="password", username="test")

        assert str(excinfo.value) == "Email is required"

        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(email=None, password="password", username="test")

        assert str(excinfo.value) == "Email is required"

    def test_create_superuser_success(self):
        """
        Verifica la creazione corretta di un Superuser.
        Deve avere is_staff=True e is_superuser=True di default.
        """
        user = User.objects.create_superuser(
            email="super@user.com",
            password="foo",
            username="superuser"
        )

        assert user.email == "super@user.com"
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_fails_if_is_staff_false(self):
        """
        Verifica che non sia possibile creare un superuser con is_staff=False.
        """
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(
                email="super@user.com",
                password="foo",
                username="superuser",
                is_staff=False  # Forziamo l'errore
            )

        assert str(excinfo.value) == "Superuser must have is_staff=True."

    def test_create_superuser_fails_if_is_superuser_false(self):
        """
        Verifica che non sia possibile creare un superuser con is_superuser=False.
        """
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(
                email="super@user.com",
                password="foo",
                username="superuser",
                is_superuser=False  # Forziamo l'errore
            )

        assert str(excinfo.value) == "Superuser must have is_superuser=True."
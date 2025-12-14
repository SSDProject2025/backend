import pytest
from django.contrib.auth import get_user_model
from fiordispino.serializers.user_serializer import RegisterSerializer

User = get_user_model()


@pytest.mark.django_db
class TestRegisterSerializer:

    def test_serializer_with_valid_data(self):
        """
        Verifica che il serializer accetti dati validi e crei l'utente correttamente.
        """
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is True

        user = serializer.save()

        # Verifica che l'utente sia stato creato nel DB
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        # Verifica che la password sia hashata e non in chiaro
        assert user.check_password("StrongPassword123!") is True
        assert user.password != "StrongPassword123!"

    def test_serializer_passwords_mismatch(self):
        """
        Verifica che venga sollevato un errore se password e password2 non coincidono.
        """
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "PasswordA",
            "password2": "PasswordB"  # Diversa
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors
        assert str(serializer.errors["password"][0]) == "The passwords do not match."

    def test_serializer_email_already_exists(self):
        """
        Verifica che il UniqueValidator funzioni e restituisca il messaggio custom.
        """
        # Creiamo prima un utente esistente
        User.objects.create_user(
            username="olduser",
            email="duplicate@example.com",
            password="password123"
        )

        data = {
            "username": "newuser",
            "email": "duplicate@example.com",  # Email duplicata
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "email" in serializer.errors
        # Verifica il messaggio personalizzato definito nel serializer
        assert str(serializer.errors["email"][0]) == "This email has already been used"

    def test_serializer_password_validation_integration(self):
        """
        Verifica che i validatori di Django (es. lunghezza minima) vengano
        catturati e convertiti in errori del serializer.
        NOTA: Questo test dipende dalla configurazione in settings.py
        """
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",  # Troppo corta (di default Django chiede 8 caratteri)
            "password2": "123"
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors
        # Verifica che ci sia un messaggio di errore (il testo esatto dipende da Django/lingua)
        assert len(serializer.errors["password"]) > 0

    def test_serializer_password_similarity_validation(self):
        """
        Verifica che la password non possa essere troppo simile allo username.
        Questo testa se stiamo passando correttamente l'oggetto 'user'
        a 'validate_password' dentro il metodo validate().
        """
        data = {
            "username": "mario",
            "email": "mario@example.com",
            "password": "mario",  # Uguale allo username
            "password2": "mario"
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors
        # Ci aspettiamo che il validatore di similarità scatti
        # Nota: Richiede che UserAttributeSimilarityValidator sia attivo nei settings

    def test_serializer_missing_required_fields(self):
        """
        Verifica che username ed email siano obbligatori.
        """
        data = {
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "username" in serializer.errors
        assert "email" in serializer.errors
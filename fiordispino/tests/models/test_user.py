import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from mixer.backend.django import mixer
from fiordispino.tests.utils_testing import *
User = get_user_model()

@pytest.mark.django_db
class TestUserModel:

    def test_string_representation(self):
        # __str__ must return the email
        user = mixer.blend(User, email="test@example.com")
        assert str(user) == "test@example.com"

    def test_email_unique(self):
        # Email must be unique
        email = "unique@example.com"
        mixer.blend(User, email=email)

        with pytest.raises(IntegrityError):
            User.objects.create_user(email=email, password="pwd", username="other")

    def test_username_unique(self):
        # Username must be unique (unique=True)
        username = "mario_rossi"
        mixer.blend(User, username=username)

        with pytest.raises(IntegrityError):
            User.objects.create_user(email="other@ex.com", password="pwd", username=username)

    def test_username_not_null(self):
        # Username cannot be None (null=False)
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="n@ex.com", password="pwd", username=None)

    def test_fields_config(self):
        # Check USERNAME_FIELD and REQUIRED_FIELDS
        assert User.USERNAME_FIELD == 'email'
        assert 'username' in User.REQUIRED_FIELDS
        assert 'email' not in User.REQUIRED_FIELDS

    def test_app_label(self):
        # Verify correct app label
        assert User._meta.app_label == 'fiordispino'
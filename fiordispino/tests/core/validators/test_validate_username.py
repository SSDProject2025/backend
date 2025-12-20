import pytest

from fiordispino.core.exceptions import UsernameValidationError
from fiordispino.core.validators import validate_username


class TestValidateUsername:
    def test_username_must_not_be_empty(self):
        with pytest.raises(UsernameValidationError):
            validate_username("")

    def test_username_must_not_contain_spaces(self):
        with pytest.raises(UsernameValidationError):
            validate_username("invalid user")

    def test_username_must_not_contain_illegal_special_characters(self):
        invalid_chars = ["user/name", "user!name", "user#name", "user?name"]
        for username in invalid_chars:
            with pytest.raises(UsernameValidationError):
                validate_username(username)

    def test_username_must_not_raise_exception_on_correct_creation(self):
        validate_username("ValidUser123")

        # case with special characters allowed (@, ., +, -, _)
        validate_username("user.name")
        validate_username("user-name")
        validate_username("user_name")
        validate_username("user@name+tag")
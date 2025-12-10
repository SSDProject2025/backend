import pytest
import re

from fiordispino.core.utils import pattern

class TestPatternUtility:

    def test_pattern_matches_valid_strings(self):
        is_number = pattern(r'\d+')

        assert is_number("123") is True
        assert is_number("0") is True
        assert is_number("999999") is True

    def test_pattern_rejects_invalid_strings(self):
        is_number = pattern(r'\d+')

        assert is_number("abc") is False
        assert is_number("123a") is False
        assert is_number("") is False

    def test_pattern_enforces_full_match(self):
        # this test make sure that it is a full match, meaning that if just a part of the string matches the method should fail

        validator = pattern(r'test')
        assert validator("test") is True

        assert validator("test case") is False
        assert validator("this is a test") is False


    def test_pattern_raises_error_on_invalid_regex_syntax(self):
       # verify that the methods fails with an invalid regex
        with pytest.raises(re.error):
            pattern(r'[unclosed-bracket')

    @pytest.mark.parametrize("regex, value, expected", [
        (r'\w+@\w+\.\w+', "email@example.com", True),  # Email semplice
        (r'\w+@\w+\.\w+', "not-an-email", False),
        (r'[A-Z]{3}', "ABC", True),  # Esattamente 3 maiuscole
        (r'[A-Z]{3}', "ABCD", False),  # Troppo lungo (fullmatch)
        (r'[A-Z]{3}', "AB", False),  # Troppo corto
    ])
    def test_various_patterns_via_parametrization(self, regex, value, expected):
        validator = pattern(regex)
        assert validator(value) is expected
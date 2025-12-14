import pytest
import re

from fiordispino.core.utils import pattern, encode_image_to_base64
import pytest
import base64
from django.core.files.uploadedfile import SimpleUploadedFile
from mixer.backend.django import mixer
from fiordispino.core.exceptions import ImageEncoderException

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


@pytest.mark.django_db
class TestImageEncoder:

    def test_encode_valid_image_success(self):
        # these raw bytes represent a 1x1 image
        small_gif_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\x00\x00'
            b'\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )

        # upload the file in memory so that django accept it
        image_file = SimpleUploadedFile(
            name='test_image.gif',
            content=small_gif_content,
            content_type='image/gif'
        )

        # the title is necessary because the image will have the game's name in path, if mixer genereates a name which is too long the operation
        # will be considered as suspicious and aborted
        game = mixer.blend('fiordispino.Game', title="game" , box_art=image_file, global_rating=5.0)

        result = encode_image_to_base64(game.box_art)

        expected_base64 = base64.b64encode(small_gif_content).decode('utf-8')

        assert isinstance(result, str)
        assert result == expected_base64

    def test_encode_raises_exception_if_field_is_empty(self):
        game = mixer.blend('fiordispino.Game', title="title", box_art=None, global_rating=5.0)

        with pytest.raises(ImageEncoderException):
            encode_image_to_base64(game.box_art)

    def test_encode_raises_generic_exception_on_io_error(self):
        # if the game is not present in memory throw an exception

        image_file = SimpleUploadedFile("test.jpg", b"dummy_content", content_type="image/jpeg")
        game = mixer.blend('fiordispino.Game', title="title", box_art=image_file, global_rating=5.0)

        game.box_art.storage.delete(game.box_art.name)

        with pytest.raises(ImageEncoderException):
            encode_image_to_base64(game.box_art)

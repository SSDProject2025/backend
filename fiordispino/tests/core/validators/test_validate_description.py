from fiordispino.core.validators import validate_game_description
from fiordispino.core.exceptions import *
import pytest

class TestValidateDescription:

    def test_validate_game_description_should_fail_with_no_description(self):
        with pytest.raises(NoDescriptionProvided):
            validate_game_description('')

    def test_validate_game_description_should_fail_with_long_description(self):
        with pytest.raises(DescriptionTooLong):
            validate_game_description('a'*201)


    @pytest.mark.parametrize(
        "description",
        [
            "<> this game is very bad!",
            "# this game is very good!",
            "@@@@ this game is ok...",
        ]
    )
    def test_validate_game_description_should_fail_with_invalid_characters(self, description):
        with pytest.raises(GameDescriptionException):
            validate_game_description(description)

    @pytest.mark.parametrize(
        "description",
        [
            "this game is very bad!",
            "this game is very good!",
            "this game is ok...",
        ]
    )
    def test_validate_game_description_should_success_with_valid_characters(self, description):
        validate_game_description(description)

import pytest

from fiordispino.core.exceptions import GameTitleException, NoTitleProvided
import fiordispino.core.validators
from fiordispino.core.validators import validate_title


class TestValidateGameTitle:

    def test_game_title_creation_failed_on_min_length(self):
        with pytest.raises(NoTitleProvided):
            validate_title('')

    def test_game_title_creation_failed_on_max_length(self):
        with pytest.raises(GameTitleException):
            validate_title('a'*1000)

    def test_game_title_creation_failed_on_invalid_title(self):
        with pytest.raises(GameTitleException):
            validate_title("a#")

    def test_game_title_creation_successful(self):
        validate_title("Call Of Duty: Black Ops III")

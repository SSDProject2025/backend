import pytest

from fiordispino.core.exceptions import PegiException
from fiordispino.core.validators import validate_pegi


class TestValidatePegi:
    def test_pegi_creation_failing_on_invalid_values(self):
        invalid_values = list(range(-1, 3)) + list(range(4, 7)) + list(range(8, 12)) + list(range(13, 16)) + [17]
        for value in invalid_values:
            with pytest.raises(PegiException):
                validate_pegi(value)

    def test_pegi_creation_successful(self):
        valid_values = [3, 7, 12, 16, 18]
        for value in valid_values:
            validate_pegi(value)
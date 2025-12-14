import pytest
from typeguard import TypeCheckError

from fiordispino.core.validators import validate_global_rating
from fiordispino.core.exceptions import GlobalRatingException


class TestValidateGlobalRating:

    def test_validate_global_rating_should_fail_with_negative_value(self):
        with pytest.raises(GlobalRatingException):
            validate_global_rating(value=-1)

    def test_validate_global_rating_should_fail_with_non_numeric_value(self):
        with pytest.raises(TypeCheckError):
            validate_global_rating(value='4.2')

    def test_validate_global_rating_should_fail_with_bigger_than_ten_value(self):
        with pytest.raises(GlobalRatingException):
            validate_global_rating(value=42)

    @pytest.mark.parametrize("rating", [
        0.0, 10.0, 0, 10, 5.5, 7.2, 4.2, 8
    ])
    def test_validate_global_rating_should_work_with_valid_values(self, rating):
        validate_global_rating(value=rating)

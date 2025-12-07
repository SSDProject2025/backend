import pytest

from fiordispino.core.exceptions import PublisherException, NoPublisherProvided
from fiordispino.core.validators import validate_publisher


class TestValidatePublisher:
    def test_publisher_must_not_be_empty(self):
        with pytest.raises(NoPublisherProvided):
            validate_publisher("")

    def test_publisher_must_not_exceed_max_length(self):
        with pytest.raises(PublisherException):
            validate_publisher('a'*1000)


    def test_publisher_must_not_contain_invalid_characters(self):
        with pytest.raises(PublisherException):
            validate_publisher("Bethesda Softworks<>!@")


    def test_publisher_must_not_raise_exception_on_correct_creation(self):
        validate_publisher("Bethesda Softworks")




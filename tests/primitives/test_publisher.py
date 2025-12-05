import pytest

from primitives.exceptions import PublisherException
from primitives.publisher import Publisher


def test_publisher_must_not_be_empty():
    with pytest.raises(PublisherException):
        Publisher("")


def test_publisher_must_not_exceed_max_length():
    with pytest.raises(PublisherException):
        Publisher("a"*101)


def test_publisher_must_not_contain_invalid_characters():
    with pytest.raises(PublisherException):
        Publisher("<Bethesda Softworks>")


def test_publisher_must_not_raise_exception_on_correct_creation():
    Publisher("Bethesda Softworks")


def test_publisher_str_method_on_correct_creation():
    assert str(Publisher("Bethesda Softworks")) == "Bethesda Softworks"
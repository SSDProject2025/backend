from fiordispino.core.exceptions import *
from valid8 import validate
from .utils import *

@typechecked
def validate_publisher(value: str) -> None:
    if not value or len(value) == 0:
        raise NoPublisherProvided("You must provide a publisher")
    if not value[0].isupper():
        raise PublisherMustBeCapitalized("The publisher name must be capitalized")

    try:
        validate("publisher", value, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z0-9\s]*'))
    except:
        raise PublisherException("Invalid publisher")


@typechecked
def validate_pegi(value: int) -> None:
    try:
        validate("pegi_ranking", value, is_in=[3, 7, 12, 16, 18])
    except:
        raise PegiException("Please note that pegi must be a value in: 3, 7, 12, 16, 18")


@typechecked
def validate_vote(value: int) -> None:
    try:
        validate("vote", value, min_value=1, max_value=10)
    except:
        raise VoteException("Please note that vote must be an integer between 1 and 10 (extremes inclusive)")


@typechecked
def validate_title(value: str) -> None:
    if not value or len(value) == 0:
        raise NoTitleProvided("You must provide a title")

    try:
        validate("title", value, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z0-9\s:]*'))
    except:
        raise GameTitleException("Invalid title")
from fiordispino.core.exceptions import *
from valid8 import validate
from .utils import *
from decimal import Decimal
from typing import Union

@typechecked
def validate_publisher(value: str) -> None:
    if not value or len(value) == 0:
        raise NoPublisherProvided("You must provide a publisher")
    if not value[0].isupper():
        raise PublisherMustBeCapitalized("The publisher name must be capitalized")

    if len(value) > 100:
        raise PublisherTooLong("Please keep publisher under 100 characters")

    try:
        validate("publisher", value, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z0-9\s]*'))
    except:
        raise PublisherException("Invalid publisher, please note that special characters are not allowed")


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
        raise GameTitleException("Invalid title, please please keep it under 100 characters and note the special characters are not allowed")


@typechecked
def validate_genre(value: str) -> None:
    if not value or len(value) == 0:
        raise NoGenreProvided("You must provide a genre")

    if len(value) > 100:
        raise GenreTooLong("Please keep genre under 100 characters")

    try:
        validate("genre", value, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z\s]*'))
    except:
        raise GenreException("Invalid genre, please note that special characters and numbers are not allowed")

@typechecked
def validate_game_description(value: str) -> None:
    if not value or len(value) == 0:
        raise NoDescriptionProvided("You must provide a game description")

    if len(value) > 200:
        raise DescriptionTooLong("Please keep game description under 200 characters")

    try:
        # this regex includes many characters for different alphabets, numbers, spaces, punctuation and limits special characters
        validate("game_description", value, min_len=1, max_len=200, custom=pattern(r'^[\w\s!,;:.?\'"()-]*$'))
    except:
        raise GameDescriptionException("Invalid game description note that some characters are not allowed")


@typechecked
def validate_global_rating(value: Union[float, Decimal]) -> None:
    try:
        validate("global_rating", value, min_value=0.0, max_value=10.0)
    except:
        raise GlobalRatingException("Global rating must be a value between 0 and 10")
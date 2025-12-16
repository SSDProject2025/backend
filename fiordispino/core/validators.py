from fiordispino.core.exceptions import *
from valid8 import validate, ValidationError as Valid8Err
from .utils import *
from decimal import Decimal
from typing import Union
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError

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
    except Valid8Err:
        raise PublisherException("Invalid publisher, please note that special characters are not allowed")


@typechecked
def validate_pegi(value: int) -> None:
    try:
        validate("pegi_ranking", value, is_in=[3, 7, 12, 16, 18])
    except Valid8Err:
        raise PegiException("Please note that pegi must be a value in: 3, 7, 12, 16, 18")


@typechecked
def validate_vote(value: int) -> None:
    try:
        validate("vote", value, min_value=1, max_value=10)
    except Valid8Err:
        raise VoteException("Please note that vote must be an integer between 1 and 10 (extremes inclusive)")


@typechecked
def validate_title(value: str) -> None:
    if not value or len(value) == 0:
        raise NoTitleProvided("You must provide a title")

    try:
        validate("title", value, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z0-9\s:]*'))
    except Valid8Err:
        raise GameTitleException("Invalid title, please please keep it under 100 characters and note the special characters are not allowed")


@typechecked
def validate_genre(value: str) -> None:
    if not value or len(value) == 0:
        raise NoGenreProvided("You must provide a genre")

    if len(value) > 100:
        raise GenreTooLong("Please keep genre under 100 characters")

    try:
        validate("genre", value, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z\s]*'))
    except Valid8Err:
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
    except Valid8Err:
        raise GameDescriptionException("Invalid game description note that some characters are not allowed")


@typechecked
def validate_global_rating(value: Union[float, Decimal]) -> None:
    try:
        validate("global_rating", value, min_value=0.0, max_value=10.0)
    except Valid8Err:
        raise GlobalRatingException("Global rating must be a value between 0 and 10")

@typechecked
def validate_username(value: str) -> None:
    validator = ASCIIUsernameValidator() # django default username validator
    try:
        validator(value)
    except ValidationError:
        raise UsernameValidationError({"detail": "Invalid username format."})

@typechecked
def validate_random_games_limit(value: str) -> None:
    try:
        # from the api you will receive a string value, first convert it to int, then validate it
        n_games = int(value)

        # at least 1 game
        # at most 20 not to overload the db
        validate("n_games", n_games, min_value=1, max_value=20)
    except (Valid8Err, ValueError, TypeError):
        raise InvalidNumberOfGamesException()

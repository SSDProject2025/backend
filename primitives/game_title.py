from dataclasses import dataclass
from typeguard import typechecked
from valid8 import validation, ValidationError, validate

from primitives.exceptions import GameTitleException
from utils.regex import pattern


@typechecked
@dataclass(frozen=True, order=True)
class GameTitle:
    title: str

    def __post_init__(self):
        try:
            validate("title", self.title, min_len=1, max_len=100, custom=pattern(r'[a-zA-Z0-9\s:]*'))
        except ValidationError as _:
            raise GameTitleException

    def __str__(self):
        return self.title
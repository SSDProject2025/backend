from dataclasses import dataclass

from typeguard import typechecked
from valid8 import validate, ValidationError

from primitives.exceptions import PegiException


@typechecked
@dataclass(frozen=True, order=True)
class Pegi:
    pegi_ranking_int: int

    def __post_init__(self):
        try:
            validate("pegi_ranking", self.pegi_ranking_int, is_in=[3, 7, 12, 16, 18])
        except ValidationError:
            raise PegiException

    def __str__(self):
        return f"PEGI {self.pegi_ranking_int}"
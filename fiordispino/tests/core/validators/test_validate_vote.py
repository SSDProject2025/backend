import pytest

from fiordispino.core.exceptions import VoteException
from fiordispino.core.validators import validate_vote

class TestValidateVote:
    def test_vote_creation_failed_on_min_value(self):
        with pytest.raises(VoteException):
            validate_vote(0)

    def test_vote_creation_failed_on_max_value(self):
        with pytest.raises(VoteException):
            validate_vote(11)

    def test_vote_creation_successful(self):
        valid_values = range(1, 11)
        for value in valid_values:
            validate_vote(value)

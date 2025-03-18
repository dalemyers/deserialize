"""Test deserializing."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, allow_unhandled, UnhandledFieldException

# pylint: enable=wrong-import-position


class Basic:
    """Represents a basic class."""

    one: int
    two: int


@allow_unhandled("key")
class BasicWithAllowedKeys:
    """Represents a basic class."""

    one: int
    two: int


def test_unhandled() -> None:
    """Test that rectange deserialization works correctly"""

    data = [{"one": 1, "two": 2, "three": 4, "four": 4}]

    for item in data:
        with pytest.raises(UnhandledFieldException):
            _ = deserialize(Basic, item, throw_on_unhandled=True)

    data = [{"one": 1, "two": 2, "key": 4}]

    for item in data:
        _ = deserialize(BasicWithAllowedKeys, item, throw_on_unhandled=True)

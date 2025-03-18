"""Test new generic deserialization introduced in 3.9."""

import os
import sys
from typing import Any, Dict, List

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize

# pylint: enable=wrong-import-position


class ListClass:
    """Basic union example."""

    one: List[int]
    two: list[int]
    three: list


class DictClass:
    """Basic union example."""

    one: Dict[int, int]
    two: dict[int, int]
    three: dict


@pytest.mark.parametrize(
    "value",
    [{"one": [1, 2, 3], "two": [1, 2, 3], "three": [1, 2, 3]}],
)
def test_lists(value: Dict[str, Any]):
    """Test that items with a simple union property deserializes."""

    instance = deserialize(ListClass, value)
    assert value["one"] == instance.one
    assert value["two"] == instance.two
    assert value["three"] == instance.three


@pytest.mark.parametrize(
    "value",
    [
        {
            "one": {1: 2, 2: 4, 3: 6},
            "two": {1: 2, 2: 4, 3: 6},
            "three": {1: 2, 2: 4, 3: 6},
        }
    ],
)
def test_dicts(value: Dict[str, Any]):
    """Test that items with a simple union property deserializes."""

    instance = deserialize(DictClass, value)
    assert value["one"] == instance.one
    assert value["two"] == instance.two
    assert value["three"] == instance.three

"""Test base types."""

import datetime
import os
import sys
from typing import Callable, List, Optional

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, DeserializeException, InvalidBaseTypeException

# pylint: enable=wrong-import-position


class Item:
    """Sample item for use in tests."""

    field: int


class Empty:
    """Sample empty item"""


def test_dicts() -> None:
    """Test that root dicts deserialize correctly."""

    data = {"field": 1}

    instance = deserialize(Item, data)
    assert data["field"] == instance.field


def test_empty_classes() -> None:
    """Test that empty classes throw an exception on deserialization."""

    data: dict[str, str] = {}

    with pytest.raises(DeserializeException):
        _ = deserialize(Empty, data)


def test_lists() -> None:
    """Test that root lists deserialize correctly."""

    data = [{"field": 1}]

    instances = deserialize(List[Item], data)

    assert len(instances) == 1
    assert instances[0].field == data[0]["field"]


def test_list_of_lists() -> None:
    """Test that root lists deserialize correctly."""

    data = [[{"field": 1}]]

    instances = deserialize(List[List[Item]], data)

    assert len(instances) == 1
    assert len(instances[0]) == 1
    assert instances[0][0].field == data[0][0]["field"]


def test_list_of_optionals() -> None:
    """Test that root lists deserialize correctly."""

    data = [1, None, 3, None, 5, None]

    instances = deserialize(List[Optional[int]], data)

    assert instances == data


def test_base_type_lists() -> None:
    """Test that lists of base types parse."""

    data = [1, 2, 3]

    parsed = deserialize(List[int], data)
    assert data == parsed


def test_base_type() -> None:
    """Test that base types don't parse."""

    base_types = [
        (1, int),
        ("Hello", str),
        (lambda x: x * 2, Callable),
        (3.14159, float),
        (datetime.datetime.now(), datetime.datetime),
        (set([]), set),
        ((1, 2), tuple),
        (range(3), range),
    ]

    for base_value, base_type in base_types:
        with pytest.raises(InvalidBaseTypeException):
            _ = deserialize(base_type, base_value)

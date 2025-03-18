"""Test deserializing tuples."""

import os
import sys
from typing import Any, Optional, Tuple, Type, Union

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, DeserializeException

# pylint: enable=wrong-import-position


class BasicUnionClassOld:
    """Basic union example."""

    one: Union[str, int]


class SomeUnionClassOld:
    """Union example."""

    one: Union[str, int]
    two: Union[int, str]
    three: Union[int, Optional[str]]


class BasicUnionClassNew:
    """Basic union example."""

    one: str | int


class SomeUnionClassNew:
    """Union example."""

    one: str | int
    two: int | str
    three: int | str | None


@pytest.mark.parametrize(
    "union_class",
    [BasicUnionClassOld, BasicUnionClassNew],
)
def test_union_simple(union_class: Type):
    """Test that items with a simple union property deserializes."""
    valid_test_cases: list[dict[str, Any]] = [
        {"one": 1},
        {"one": "1"},
    ]

    invalid_test_cases: list[dict[str, Any]] = [
        {"one": 3.1415},
        {"one": None},
        {"one": union_class()},
    ]

    for valid_test_case in valid_test_cases:
        instance = deserialize(union_class, valid_test_case)
        assert valid_test_case["one"] == instance.one

    for invalid_test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(union_class, invalid_test_case)


@pytest.mark.parametrize(
    "union_classes",
    [
        (BasicUnionClassOld, SomeUnionClassOld),
        (BasicUnionClassNew, SomeUnionClassNew),
    ],
)
def test_union(union_classes: Tuple[Type, Type]):
    """Test that items with union properties deserializes."""

    basic_union_class, some_union_class = union_classes

    valid_test_cases: list[dict[str, Any]] = [
        {"one": 1, "two": 2, "three": 3},
        {"one": 1, "two": "2", "three": 3},
        {"one": "1", "two": 2, "three": 3},
        {"one": "1", "two": "2", "three": 3},
        {"one": 1, "two": 2, "three": None},
        {"one": 1, "two": "2", "three": None},
        {"one": "1", "two": 2, "three": None},
        {"one": "1", "two": "2", "three": None},
        {"one": 1, "two": 2, "three": "3"},
        {"one": 1, "two": "2", "three": "3"},
        {"one": "1", "two": 2, "three": "3"},
        {"one": "1", "two": "2", "three": "3"},
    ]

    invalid_test_cases: list[dict[str, Any]] = [
        {"one": None, "two": 2, "three": 3},
        {"one": 1, "two": None, "three": 3},
        {"one": 1, "two": 2, "three": basic_union_class()},
    ]

    for valid_test_case in valid_test_cases:
        instance = deserialize(some_union_class, valid_test_case)
        assert valid_test_case["one"] == instance.one
        assert valid_test_case["two"] == instance.two
        assert valid_test_case["three"] == instance.three

    for invalid_test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(some_union_class, invalid_test_case)

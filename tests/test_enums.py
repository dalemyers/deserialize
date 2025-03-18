"""Test deserializing enums."""

import enum
import os
import sys
from typing import Any, List, Optional

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, DeserializeException

# pylint: enable=wrong-import-position


class SomeStringEnum(enum.Enum):
    """Enum example."""

    ONE = "One"
    TWO = "Two"
    THREE = "Three"


class SomeIntEnum(enum.Enum):
    """Enum example."""

    ONE = 1
    TWO = 2
    THREE = 3


class SomeClass:
    """Simple enum test class."""

    my_value: int
    my_enum: SomeStringEnum
    my_optional_enum: Optional[SomeIntEnum]


def test_enums_simple() -> None:
    """Test that items with an enum property deserializes."""
    valid_test_cases = [
        {"my_value": 1, "my_enum": "One", "my_optional_enum": 1},
        {"my_value": 2, "my_enum": "Two", "my_optional_enum": 2},
        {"my_value": 3, "my_enum": "Three", "my_optional_enum": None},
    ]

    invalid_test_cases = [
        {"my_value": 1, "my_enum": None, "my_optional_enum": 1},
        {"my_value": 2, "my_enum": "two", "my_optional_enum": None},
        {"my_value": 3, "my_enum": 3, "my_optional_enum": "Three"},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(SomeClass, test_case)

        assert test_case["my_value"] == instance.my_value

        if test_case["my_enum"] is None:
            assert instance.my_enum is None
        else:
            assert test_case["my_enum"] == instance.my_enum.value

        if test_case["my_optional_enum"] is None:
            assert instance.my_optional_enum is None
        else:
            assert test_case["my_optional_enum"] == instance.my_optional_enum.value

    for invalid_test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(SomeClass, invalid_test_case)


def test_enums_order() -> None:
    """Test that enum ordering is consistent and expected."""

    class OrderTest(enum.Enum):
        """Order enum test class."""

        ONE = "one"
        TWO = "one"
        THREE = "three"

    test_cases: list[list[Any]] = [
        [["one", "one", "three"], [OrderTest.ONE, OrderTest.ONE, OrderTest.THREE]]
    ]

    for test_case in test_cases:
        data = test_case[0]
        expected_result = test_case[1]

        result = deserialize(List[OrderTest], data)

        assert len(result) == len(data) == len(expected_result)
        assert result == expected_result

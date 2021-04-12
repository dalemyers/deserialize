"""Test deserializing enums."""

import enum
import os
import sys
from typing import List, Optional

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class SomeStringEnum(enum.Enum):
    """Enum example."""

    one = "One"
    two = "Two"
    three = "Three"


class SomeIntEnum(enum.Enum):
    """Enum example."""

    one = 1
    two = 2
    three = 3


class SomeClass:
    """Simple enum test class."""

    my_value: int
    my_enum: SomeStringEnum
    my_optional_enum: Optional[SomeIntEnum]


def test_enums_simple():
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
        instance = deserialize.deserialize(SomeClass, test_case)

        assert test_case["my_value"] == instance.my_value

        if test_case["my_enum"] is None:
            assert instance.my_enum is None
        else:
            assert test_case["my_enum"] == instance.my_enum.value

        if test_case["my_optional_enum"] is None:
            assert instance.my_optional_enum is None
        else:
            assert test_case["my_optional_enum"] == instance.my_optional_enum.value

    for test_case in invalid_test_cases:
        with pytest.raises(deserialize.DeserializeException):
            _ = deserialize.deserialize(SomeClass, test_case)


def test_enums_order():
    """Test that enum ordering is consistent and expected."""

    class OrderTest(enum.Enum):
        """Order enum test class."""

        one = "one"
        two = "one"
        three = "three"

    test_cases = [[["one", "one", "three"], [OrderTest.one, OrderTest.one, OrderTest.three]]]

    for test_case in test_cases:

        data = test_case[0]
        expected_result = test_case[1]

        result = deserialize.deserialize(List[OrderTest], data)

        assert len(result) == len(data) == len(expected_result)
        assert result == expected_result

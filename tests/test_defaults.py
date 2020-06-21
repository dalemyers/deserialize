"""Test defaults."""

import os
import sys
from typing import Optional

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


@deserialize.default("two", "two")
class SampleItem:
    """Sample item for use in tests."""

    one: int
    two: str


@deserialize.default("two", "two")
class SampleOptionalItem:
    """Sample item for use in tests."""

    one: int
    two: Optional[str]


def test_default():
    """Test that root lists deserialize correctly."""

    test_cases = [{"one": 1, "two": "two"}, {"one": 1}]

    for test_case in test_cases:
        instance = deserialize.deserialize(SampleItem, test_case)
        assert test_case["one"] == instance.one
        assert instance.two == "two"

        optional_instance = deserialize.deserialize(SampleOptionalItem, test_case)
        assert test_case["one"] == optional_instance.one
        assert optional_instance.two == "two"

    invalid_test_cases = [{"one": 1, "two": None}]

    for test_case in invalid_test_cases:
        with pytest.raises(deserialize.DeserializeException):
            _ = deserialize.deserialize(SampleItem, test_case)

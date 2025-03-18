"""Test deserializing."""

import os
import sys
from typing import List

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, DeserializeException, auto_snake

# pylint: enable=wrong-import-position


def test_snake_case_from_camel() -> None:
    """Test that parsers are applied correctly."""

    @auto_snake()
    class SnakeCaseItem:
        """Sample item for use in tests."""

        int_field: int
        some_values: List[int]

    instance = deserialize(
        SnakeCaseItem,
        {"intField": 1, "someValues": [1, 2, 3]},
    )
    assert instance.int_field == 1
    assert instance.some_values == [1, 2, 3]


def test_snake_case_from_pascal() -> None:
    """Test that parsers are applied correctly."""

    @auto_snake()
    class SnakeCaseItem:
        """Sample item for use in tests."""

        int_field: int
        some_values: List[int]

    instance = deserialize(
        SnakeCaseItem,
        {"IntField": 1, "SomeValues": [1, 2, 3]},
    )
    assert instance.int_field == 1
    assert instance.some_values == [1, 2, 3]


def test_snake_case_non_snake_property() -> None:
    """Test that parsers are applied correctly."""

    @auto_snake()
    class SnakeCaseItem:
        """Sample item for use in tests."""

        intField: int
        some_values: List[int]

    with pytest.raises(DeserializeException):
        _ = deserialize(
            SnakeCaseItem,
            {"IntField": 1, "SomeValues": [1, 2, 3]},
        )


def test_non_snake_case() -> None:
    """Test that parsers are applied correctly."""

    class SnakeCaseItem:
        """Sample item for use in tests."""

        int_field: int
        some_values: List[int]

    with pytest.raises(DeserializeException):
        _ = deserialize(
            SnakeCaseItem,
            {"IntField": 1, "SomeValues": [1, 2, 3]},
        )


def test_nested_snake_case() -> None:
    """Test that parsers are applied correctly."""

    @auto_snake()
    class SnakeCaseItem:
        """Sample item for use in tests."""

        int_field: int
        some_values: List[int]

    class NonSnakeCaseItem:
        """Sample item for use in tests."""

        snake_item: SnakeCaseItem

    instance = deserialize(
        NonSnakeCaseItem, {"snake_item": {"IntField": 1, "SomeValues": [1, 2, 3]}}
    )
    assert instance.snake_item.int_field == 1
    assert instance.snake_item.some_values == [1, 2, 3]


def test_nested_snake_case_failure() -> None:
    """Test that parsers are applied correctly."""

    @auto_snake()
    class SnakeCaseItem:
        """Sample item for use in tests."""

        int_field: int
        some_values: List[int]

    class NonSnakeCaseItem:
        """Sample item for use in tests."""

        snake_item: SnakeCaseItem

    with pytest.raises(DeserializeException):
        _ = deserialize(NonSnakeCaseItem, {"SnakeItem": {"IntField": 1, "SomeValues": [1, 2, 3]}})

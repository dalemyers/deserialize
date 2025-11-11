"""Test set deserialization functionality."""

import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    DeserializeException,
    deserialize,
    is_set,
    set_content_type,
)

# pylint: enable=wrong-import-position


# ============================================================================
# Type Checking Tests
# ============================================================================


def test_is_set() -> None:
    """Test is_set."""
    assert is_set(set[int])
    assert is_set(set[str])
    assert is_set(set[set[int]])
    assert is_set(set[type(None)])  # type: ignore
    assert is_set(set[dict[str, str]])
    assert is_set(set[str | None])
    assert is_set(set)

    assert not is_set(int)
    assert not is_set(set[int] | None)
    assert not is_set(str | None)
    assert not is_set(type(None))
    assert not is_set(list[int])


def test_set_content_type() -> None:
    """Test set_content_type."""
    assert set_content_type(set[int], "") == int
    assert set_content_type(set[str], "") == str
    assert set_content_type(set[dict[str, str]], "") == dict[str, str]
    assert set_content_type(set[int | None], "") == int | None
    assert set_content_type(set[set[int]], "") == set[int]

    with pytest.raises(TypeError):
        _ = set_content_type(int, "")

    with pytest.raises(TypeError):
        _ = set_content_type(tuple[set[int], int], "")


# ============================================================================
# Basic Set Deserialization Tests
# ============================================================================


class SimpleSetClass:
    """Class with a simple set field."""

    numbers: set[int]


class MultipleSetClass:
    """Class with multiple set fields."""

    integers: set[int]
    strings: set[str]
    floats: set[float]


def test_basic_set_deserialization() -> None:
    """Test basic set deserialization from list."""
    data = {"numbers": [1, 2, 3]}
    result = deserialize(SimpleSetClass, data)

    assert isinstance(result.numbers, set)
    assert result.numbers == {1, 2, 3}


def test_set_with_duplicates() -> None:
    """Test that duplicates in list are removed when deserializing to set."""
    data = {"numbers": [1, 2, 3, 2, 1, 3]}
    result = deserialize(SimpleSetClass, data)

    assert isinstance(result.numbers, set)
    assert result.numbers == {1, 2, 3}
    assert len(result.numbers) == 3


def test_empty_set() -> None:
    """Test deserializing an empty list to an empty set."""
    data: dict[str, list[int]] = {"numbers": []}
    result = deserialize(SimpleSetClass, data)

    assert isinstance(result.numbers, set)
    assert result.numbers == set()
    assert len(result.numbers) == 0


def test_multiple_set_fields() -> None:
    """Test class with multiple set fields."""
    data = {
        "integers": [1, 2, 3, 2],
        "strings": ["a", "b", "c", "a"],
        "floats": [1.1, 2.2, 3.3, 1.1],
    }
    result = deserialize(MultipleSetClass, data)

    assert result.integers == {1, 2, 3}
    assert result.strings == {"a", "b", "c"}
    assert result.floats == {1.1, 2.2, 3.3}


# ============================================================================
# Set of Complex Types Tests
# ============================================================================


class Item:
    """Simple item for testing."""

    value: int

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Item):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class SetOfStringsClass:
    """Class with set of strings."""

    tags: set[str]


class NestedSetClass:
    """Class with nested set."""

    nested: set[frozenset[int]]


def test_set_of_strings() -> None:
    """Test set of strings."""
    data = {"tags": ["python", "rust", "go", "python"]}
    result = deserialize(SetOfStringsClass, data)

    assert result.tags == {"python", "rust", "go"}


def test_set_with_hashable_objects() -> None:
    """Test set with custom hashable objects."""

    class SetOfItemsClass:
        """Class with set of items."""

        items: set[Item]

    data = {"items": [{"value": 1}, {"value": 2}, {"value": 1}]}
    result = deserialize(SetOfItemsClass, data)

    assert len(result.items) == 2
    values = {item.value for item in result.items}
    assert values == {1, 2}


# ============================================================================
# Root-Level Set Tests
# ============================================================================


def test_root_set() -> None:
    """Test deserializing a list directly to a set."""
    data = [1, 2, 3, 2, 1]
    result = deserialize(set[int], data)

    assert isinstance(result, set)
    assert result == {1, 2, 3}


def test_root_set_of_strings() -> None:
    """Test root-level set of strings."""
    data = ["a", "b", "c", "a"]
    result = deserialize(set[str], data)

    assert result == {"a", "b", "c"}


# ============================================================================
# Optional Set Tests
# ============================================================================


class OptionalSetClass:
    """Class with optional set field."""

    numbers: set[int] | None


def test_optional_set_with_value() -> None:
    """Test optional set with a value."""
    data = {"numbers": [1, 2, 3]}
    result = deserialize(OptionalSetClass, data)

    assert result.numbers == {1, 2, 3}


def test_optional_set_with_none() -> None:
    """Test optional set with None."""
    data = {"numbers": None}
    result = deserialize(OptionalSetClass, data)

    assert result.numbers is None


# ============================================================================
# Set with Optional Elements Tests
# ============================================================================


class SetWithOptionalElementsClass:
    """Class with set of optional values."""

    values: set[int | None]


def test_set_with_none_elements() -> None:
    """Test set containing None elements."""
    data = {"values": [1, 2, None, 3, None]}
    result = deserialize(SetWithOptionalElementsClass, data)

    # Sets can contain None
    assert result.values == {1, 2, 3, None}


# ============================================================================
# Nested Collections with Sets Tests
# ============================================================================


class ListOfSetsClass:
    """Class with list of sets."""

    sets: list[set[int]]


class SetInDictClass:
    """Class with dict containing sets."""

    data: dict[str, set[int]]


def test_list_of_sets() -> None:
    """Test list containing sets."""
    data = {"sets": [[1, 2, 3], [4, 5, 6], [1, 1, 1]]}
    result = deserialize(ListOfSetsClass, data)

    assert len(result.sets) == 3
    assert result.sets[0] == {1, 2, 3}
    assert result.sets[1] == {4, 5, 6}
    assert result.sets[2] == {1}


def test_set_in_dict() -> None:
    """Test dictionary with set values."""
    data = {
        "data": {
            "a": [1, 2, 3],
            "b": [4, 5, 6, 4],
        }
    }
    result = deserialize(SetInDictClass, data)

    assert result.data["a"] == {1, 2, 3}
    assert result.data["b"] == {4, 5, 6}


# ============================================================================
# Error Cases Tests
# ============================================================================


def test_set_from_non_list_fails() -> None:
    """Test that deserializing non-list data to set fails."""
    data = {"numbers": "not a list"}

    with pytest.raises(DeserializeException):
        _ = deserialize(SimpleSetClass, data)


def test_set_with_wrong_element_type_fails() -> None:
    """Test that wrong element types cause errors."""
    data = {"numbers": ["a", "b", "c"]}

    with pytest.raises(DeserializeException):
        _ = deserialize(SimpleSetClass, data)


# ============================================================================
# Untyped Set Tests
# ============================================================================


class UntypedSetClass:
    """Class with untyped set."""

    values: set  # pyright: ignore[reportMissingTypeArgument]


def test_untyped_set() -> None:
    """Test that untyped sets work."""
    data = {"values": [1, "two", 3.0, 1]}
    result = deserialize(UntypedSetClass, data)

    assert isinstance(result.values, set)  # pyright: ignore[reportUnknownMemberType]
    # Mixed types are allowed in untyped sets
    assert result.values == {1, "two", 3.0}  # pyright: ignore[reportUnknownMemberType]

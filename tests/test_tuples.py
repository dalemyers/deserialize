"""Test tuple deserialization functionality."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    DeserializeException,
    deserialize,
    is_tuple,
    tuple_content_types,
)

# pylint: enable=wrong-import-position


# ============================================================================
# Type Checking Tests
# ============================================================================


def test_is_tuple() -> None:
    """Test is_tuple."""
    assert is_tuple(tuple[int, str])
    assert is_tuple(tuple[int, int, int])
    assert is_tuple(tuple[int, ...])
    assert is_tuple(tuple)

    assert not is_tuple(int)
    assert not is_tuple(tuple[int, str] | None)
    assert not is_tuple(str | None)
    assert not is_tuple(type(None))
    assert not is_tuple(list[int])


def test_tuple_content_types() -> None:
    """Test tuple_content_types."""
    assert tuple_content_types(tuple[int, str], "") == (int, str)
    assert tuple_content_types(tuple[int, int, int], "") == (int, int, int)
    assert tuple_content_types(tuple[int, ...], "") == (int, Ellipsis)
    assert tuple_content_types(tuple, "") == ()

    with pytest.raises(TypeError):
        _ = tuple_content_types(int, "")

    with pytest.raises(TypeError):
        _ = tuple_content_types(list[int], "")


# ============================================================================
# Fixed-Length Tuple Tests
# ============================================================================


class FixedTupleClass:
    """Class with a fixed-length tuple field."""

    coords: tuple[int, int]


class MixedTypeTupleClass:
    """Class with a mixed-type tuple field."""

    data: tuple[str, int, float, bool]


def test_fixed_length_tuple() -> None:
    """Test fixed-length tuple deserialization."""
    data = {"coords": [10, 20]}
    result = deserialize(FixedTupleClass, data)

    assert isinstance(result.coords, tuple)
    assert result.coords == (10, 20)
    assert len(result.coords) == 2


def test_mixed_type_tuple() -> None:
    """Test tuple with mixed types."""
    data = {"data": ["hello", 42, 3.14, True]}
    result = deserialize(MixedTypeTupleClass, data)

    assert isinstance(result.data, tuple)
    assert result.data == ("hello", 42, 3.14, True)
    assert len(result.data) == 4


def test_fixed_length_mismatch_too_short() -> None:
    """Test that too few elements raises error."""
    data = {"coords": [10]}

    with pytest.raises(DeserializeException) as exc_info:
        _ = deserialize(FixedTupleClass, data)

    assert "length 1" in str(exc_info.value)
    assert "length 2" in str(exc_info.value)


def test_fixed_length_mismatch_too_long() -> None:
    """Test that too many elements raises error."""
    data = {"coords": [10, 20, 30]}

    with pytest.raises(DeserializeException) as exc_info:
        _ = deserialize(FixedTupleClass, data)

    assert "length 3" in str(exc_info.value)
    assert "length 2" in str(exc_info.value)


def test_fixed_tuple_wrong_types() -> None:
    """Test that wrong element types cause errors."""
    data = {"coords": ["a", "b"]}

    with pytest.raises(DeserializeException):
        _ = deserialize(FixedTupleClass, data)


# ============================================================================
# Variable-Length Tuple Tests
# ============================================================================


class VariableTupleClass:
    """Class with a variable-length tuple field."""

    numbers: tuple[int, ...]


class VariableStringTupleClass:
    """Class with a variable-length string tuple field."""

    tags: tuple[str, ...]


def test_variable_length_tuple() -> None:
    """Test variable-length tuple deserialization."""
    data = {"numbers": [1, 2, 3, 4, 5]}
    result = deserialize(VariableTupleClass, data)

    assert isinstance(result.numbers, tuple)
    assert result.numbers == (1, 2, 3, 4, 5)
    assert len(result.numbers) == 5


def test_variable_length_tuple_empty() -> None:
    """Test empty variable-length tuple."""
    data: dict[str, list[int]] = {"numbers": []}
    result = deserialize(VariableTupleClass, data)

    assert isinstance(result.numbers, tuple)
    assert result.numbers == ()
    assert len(result.numbers) == 0


def test_variable_length_tuple_single() -> None:
    """Test variable-length tuple with single element."""
    data = {"numbers": [42]}
    result = deserialize(VariableTupleClass, data)

    assert result.numbers == (42,)
    assert len(result.numbers) == 1


def test_variable_string_tuple() -> None:
    """Test variable-length tuple with strings."""
    data = {"tags": ["python", "rust", "go"]}
    result = deserialize(VariableStringTupleClass, data)

    assert result.tags == ("python", "rust", "go")


def test_variable_tuple_wrong_types() -> None:
    """Test that wrong element types cause errors."""
    data = {"numbers": [1, 2, "three"]}

    with pytest.raises(DeserializeException):
        _ = deserialize(VariableTupleClass, data)


# ============================================================================
# Root-Level Tuple Tests
# ============================================================================


def test_root_fixed_tuple() -> None:
    """Test deserializing a list directly to a fixed tuple."""
    data = [1, "hello", 3.14]
    result = deserialize(tuple[int, str, float], data)

    assert isinstance(result, tuple)
    assert result == (1, "hello", 3.14)


def test_root_variable_tuple() -> None:
    """Test deserializing a list directly to a variable tuple."""
    data = ["a", "b", "c", "d"]
    result = deserialize(tuple[str, ...], data)

    assert isinstance(result, tuple)
    assert result == ("a", "b", "c", "d")


# ============================================================================
# Optional Tuple Tests
# ============================================================================


class OptionalTupleClass:
    """Class with optional tuple field."""

    coords: tuple[int, int] | None


def test_optional_tuple_with_value() -> None:
    """Test optional tuple with a value."""
    data = {"coords": [5, 10]}
    result = deserialize(OptionalTupleClass, data)

    assert result.coords == (5, 10)


def test_optional_tuple_with_none() -> None:
    """Test optional tuple with None."""
    data = {"coords": None}
    result = deserialize(OptionalTupleClass, data)

    assert result.coords is None


# ============================================================================
# Nested Tuple Tests
# ============================================================================


class NestedTupleClass:
    """Class with nested tuples."""

    matrix: list[tuple[int, int]]


class TupleInDictClass:
    """Class with dict containing tuples."""

    data: dict[str, tuple[int, int]]


def test_list_of_tuples() -> None:
    """Test list containing tuples."""
    data = {"matrix": [[1, 2], [3, 4], [5, 6]]}
    result = deserialize(NestedTupleClass, data)

    assert len(result.matrix) == 3
    assert result.matrix[0] == (1, 2)
    assert result.matrix[1] == (3, 4)
    assert result.matrix[2] == (5, 6)


def test_tuple_in_dict() -> None:
    """Test dictionary with tuple values."""
    data = {"data": {"a": [1, 2], "b": [3, 4]}}
    result = deserialize(TupleInDictClass, data)

    assert result.data["a"] == (1, 2)
    assert result.data["b"] == (3, 4)


# ============================================================================
# Complex Nested Types Tests
# ============================================================================


class Item:
    """Simple item for testing."""

    value: int


class TupleOfObjectsClass:
    """Class with tuple of custom objects."""

    items: tuple[Item, Item]


def test_tuple_of_objects() -> None:
    """Test tuple with custom objects."""
    data = {"items": [{"value": 1}, {"value": 2}]}
    result = deserialize(TupleOfObjectsClass, data)

    assert len(result.items) == 2
    assert result.items[0].value == 1
    assert result.items[1].value == 2


# ============================================================================
# Untyped Tuple Tests
# ============================================================================


class UntypedTupleClass:
    """Class with untyped tuple."""

    values: tuple  # pyright: ignore[reportMissingTypeArgument]


def test_untyped_tuple() -> None:
    """Test that untyped tuples work."""
    data = {"values": [1, "two", 3.0]}
    result = deserialize(UntypedTupleClass, data)

    assert isinstance(result.values, tuple)  # pyright: ignore[reportUnknownMemberType]
    assert result.values == (1, "two", 3.0)  # pyright: ignore[reportUnknownMemberType]


# ============================================================================
# Error Cases Tests
# ============================================================================


def test_tuple_from_non_list_fails() -> None:
    """Test that deserializing non-list data to tuple fails."""
    data = {"coords": "not a list"}

    with pytest.raises(DeserializeException):
        _ = deserialize(FixedTupleClass, data)


# ============================================================================
# Edge Cases Tests
# ============================================================================


class SingleElementTupleClass:
    """Class with single-element tuple."""

    value: tuple[int]


def test_single_element_tuple() -> None:
    """Test tuple with single element."""
    data = {"value": [42]}
    result = deserialize(SingleElementTupleClass, data)

    assert result.value == (42,)
    assert len(result.value) == 1


def test_empty_fixed_tuple() -> None:
    """Test empty fixed-length tuple (edge case)."""

    class EmptyTupleClass:
        """Class with empty tuple."""

        value: tuple[()]  # type: ignore

    data: dict[str, list[int]] = {"value": []}
    result = deserialize(EmptyTupleClass, data)

    assert result.value == ()
    assert len(result.value) == 0


def test_nested_variable_tuples() -> None:
    """Test tuple containing variable-length tuples."""

    class NestedVarTupleClass:
        """Class with nested variable tuples."""

        data: tuple[tuple[int, ...], tuple[str, ...]]

    data = {"data": [[1, 2, 3], ["a", "b"]]}
    result = deserialize(NestedVarTupleClass, data)

    assert result.data[0] == (1, 2, 3)
    assert result.data[1] == ("a", "b")

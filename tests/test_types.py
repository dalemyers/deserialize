"""Test type handling and type checking functionality."""

import datetime
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Pattern, Union

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    DeserializeException,
    InvalidBaseTypeException,
    deserialize,
    dict_content_types,
    is_dict,
    is_list,
    is_set,
    is_tuple,
    is_typing_type,
    is_union,
    list_content_type,
    set_content_type,
    tuple_content_types,
    union_types,
)

# pylint: enable=wrong-import-position


# ============================================================================
# Type Checking Tests
# ============================================================================


def test_is_typing_type() -> None:
    """Test is_typing_type."""
    assert not is_typing_type(int)
    assert not is_typing_type(str)
    assert not is_typing_type(datetime.datetime)
    assert not is_typing_type(float)
    assert not is_typing_type(dict)
    assert not is_typing_type(list)
    assert not is_typing_type(tuple)
    assert not is_typing_type(range)

    assert is_typing_type(List)
    assert is_typing_type(list[int])
    assert is_typing_type(Dict)
    assert is_typing_type(dict[str, str])
    assert is_typing_type(int | None)
    assert is_typing_type(list[List])  # pyright: ignore[reportMissingTypeArgument]
    assert is_typing_type(tuple[str, int])
    assert is_typing_type(Union[str, None])
    assert is_typing_type(Union[str, int])
    assert is_typing_type(Callable)
    assert is_typing_type(Pattern)


def test_is_union() -> None:
    """Test is_union."""
    assert is_union(Union[int, None])
    assert is_union(Union[dict[str, str], None])
    assert is_union(Union[int, str])
    assert is_union(Union[str, int])
    assert is_union(Union[int, Union[int, str]])
    assert is_union(Union[Union[str, int], int])

    assert not is_union(int)
    assert not is_union(list[int])
    assert not is_union(dict[str, str])
    assert not is_union(tuple[int | None, int])

    # The typing module doesn't let you create either of these.
    assert not is_union(Union[None])
    assert not is_union(Union[None, None])


def test_union_types() -> None:
    """Test union_types."""
    assert union_types(Union[str, int], "") == {str, int}
    assert union_types(Union[dict[str, str], int], "") == {
        dict[str, str],
        int,
    }
    assert union_types(Union[int, None], "") == {int, type(None)}
    assert union_types(Union[None, int], "") == {type(None), int}

    # X | None | None == X | None
    assert union_types(Union[Union[int, None], None], "") == {
        int,
        type(None),
    }
    assert union_types(Union[None, str | None], "") == {type(None), str}

    with pytest.raises(DeserializeException):
        _ = union_types(int, "")

    with pytest.raises(DeserializeException):
        _ = union_types(tuple[int | None, int], "")


def test_is_list() -> None:
    """Test is_list."""
    assert is_list(list[int])
    assert is_list(list[str])
    assert is_list(list[list[int]])
    assert is_list(list[type(None)])  # type: ignore
    assert is_list(list[dict[str, str]])
    assert is_list(list[str | None])
    assert is_list(list[Union[str, int]])
    assert is_list(list)

    assert not is_list(int)
    assert not is_list(list[int] | None)
    assert not is_list(str | None)
    assert not is_list(type(None))


def test_list_content_type() -> None:
    """Test list_content_type."""
    assert list_content_type(list[int], "") == int
    assert list_content_type(list[str], "") == str
    assert list_content_type(list[dict[str, str]], "") == dict[str, str]
    assert list_content_type(list[int | None], "") == int | None
    assert list_content_type(list[list[int]], "") == list[int]

    with pytest.raises(TypeError):
        _ = list_content_type(int, "")

    with pytest.raises(TypeError):
        _ = list_content_type(tuple[list[int], int], "")


def test_is_dict() -> None:
    """Test is_dict."""
    assert is_dict(dict)
    assert is_dict(dict[int, int])
    assert is_dict(dict[str, int])
    assert is_dict(dict[str, dict[str, str]])
    assert is_dict(dict[int, str | None])
    assert is_dict(dict[dict[int, str], dict[str, int]])

    assert not is_dict(int)
    assert not is_dict(dict[int, int] | None)
    assert not is_dict(tuple[str, int])


def test_dict_content_types() -> None:
    """Test dict_content_types."""
    assert dict_content_types(dict[int, int], "") == (int, int)
    assert dict_content_types(dict[str, int], "") == (str, int)
    assert dict_content_types(dict[str, dict[str, str]], "") == (
        str,
        dict[str, str],
    )
    assert dict_content_types(dict[dict[int, int], dict[str, str]], "") == (
        dict[int, int],
        dict[str, str],
    )
    assert dict_content_types(dict[int, str | None], "") == (
        int,
        str | None,
    )

    with pytest.raises(TypeError):
        _ = dict_content_types(int, "")

    with pytest.raises(TypeError):
        _ = dict_content_types(tuple[list[int], int], "")


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
# Base Type Tests
# ============================================================================


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

    instances = deserialize(list[Item], data)

    assert len(instances) == 1
    assert instances[0].field == data[0]["field"]


def test_list_of_lists() -> None:
    """Test that root lists deserialize correctly."""
    data = [[{"field": 1}]]

    instances = deserialize(list[list[Item]], data)

    assert len(instances) == 1
    assert len(instances[0]) == 1
    assert instances[0][0].field == data[0][0]["field"]


def test_list_of_optionals() -> None:
    """Test that root lists deserialize correctly."""
    data = [1, None, 3, None, 5, None]

    instances = deserialize(list[int | None], data)

    assert instances == data


def test_base_type_lists() -> None:
    """Test that lists of base types parse."""
    data = [1, 2, 3]

    parsed = deserialize(list[int], data)
    assert data == parsed


def test_base_type() -> None:
    """Test that base types don't parse."""
    base_types = [  # pyright: ignore[reportUnknownVariableType]
        (1, int),
        ("Hello", str),
        (lambda x: x * 2, Callable),  # pyright: ignore[reportUnknownLambdaType]
        (3.14159, float),
        (datetime.datetime.now(), datetime.datetime),
        (set([]), set),
        ((1, 2), tuple),
        (range(3), range),
    ]

    for base_value, base_type in base_types:  # pyright: ignore[reportUnknownVariableType]
        with pytest.raises(InvalidBaseTypeException):
            _ = deserialize(  # pyright: ignore[reportUnknownVariableType, reportArgumentType]
                base_type,  # pyright: ignore[reportUnknownVariableType, reportArgumentType]
                base_value,  # pyright: ignore[reportUnknownVariableType, reportArgumentType]
            )


# ============================================================================
# Generic Type Tests (3.9+)
# ============================================================================


class ListClass:
    """Basic list example."""

    one: list[int]
    two: list[int]
    three: list  # pyright: ignore[reportMissingTypeArgument]


class DictClass:
    """Basic dict example."""

    one: dict[int, int]
    two: dict[int, int]
    three: dict  # pyright: ignore[reportMissingTypeArgument]


class SetClass:
    """Basic set example."""

    one: set[int]
    two: set[int]
    three: set  # pyright: ignore[reportMissingTypeArgument]


class TupleClass:
    """Basic tuple example."""

    one: tuple[int, int]
    two: tuple[int, ...]
    three: tuple  # pyright: ignore[reportMissingTypeArgument]


@pytest.mark.parametrize(
    "value",
    [{"one": [1, 2, 3], "two": [1, 2, 3], "three": [1, 2, 3]}],
)
def test_generic_lists(value: dict[str, Any]):
    """Test that items with generic list types deserialize."""
    instance = deserialize(ListClass, value)
    assert value["one"] == instance.one
    assert value["two"] == instance.two
    assert value["three"] == instance.three  # pyright: ignore[reportUnknownMemberType]


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
def test_generic_dicts(value: dict[str, Any]):
    """Test that items with generic dict types deserialize."""
    instance = deserialize(DictClass, value)
    assert value["one"] == instance.one
    assert value["two"] == instance.two
    assert value["three"] == instance.three  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    "value",
    [{"one": [1, 2, 3], "two": [1, 2, 3, 2], "three": [1, 2, 3]}],
)
def test_generic_sets(value: dict[str, Any]):
    """Test that items with generic set types deserialize."""
    instance = deserialize(SetClass, value)
    assert {1, 2, 3} == instance.one
    assert {1, 2, 3} == instance.two
    assert {1, 2, 3} == instance.three  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    "value",
    [{"one": [1, 2], "two": [1, 2, 3], "three": [1, 2, 3]}],
)
def test_generic_tuples(value: dict[str, Any]):
    """Test that items with generic tuple types deserialize."""
    instance = deserialize(TupleClass, value)
    assert (1, 2) == instance.one
    assert (1, 2, 3) == instance.two
    assert (1, 2, 3) == instance.three  # pyright: ignore[reportUnknownMemberType]


# ============================================================================
# Annotation Style Tests (Old vs New)
# ============================================================================


class OldStyleAnnotations:
    """Class using old-style typing annotations (List, Dict, Optional, etc)."""

    name: str
    age: Optional[int]
    tags: List[str]
    metadata: Dict[str, int]
    nested_lists: List[List[int]]


class NewStyleAnnotations:
    """Class using new-style typing annotations (list, dict, | None, etc)."""

    name: str
    age: int | None
    tags: list[str]
    metadata: dict[str, int]
    nested_lists: list[list[int]]


class MixedStyleAnnotations:
    """Class using a mix of old and new style annotations."""

    # New style
    name: str
    count: int | None

    # Old style
    items: List[str]
    mapping: Dict[str, int]


class NestedOldStyle:
    """Nested class with old-style annotations."""

    items: List[Dict[str, Optional[int]]]
    matrix: List[List[int]]


class NestedNewStyle:
    """Nested class with new-style annotations."""

    items: list[dict[str, int | None]]
    matrix: list[list[int]]


def test_old_style_annotations() -> None:
    """Test deserialization with old-style type annotations."""
    data = {
        "name": "Alice",
        "age": 30,
        "tags": ["python", "rust"],
        "metadata": {"score": 100, "level": 5},
        "nested_lists": [[1, 2], [3, 4]],
    }

    result = deserialize(OldStyleAnnotations, data)

    assert result.name == "Alice"
    assert result.age == 30
    assert result.tags == ["python", "rust"]
    assert result.metadata == {"score": 100, "level": 5}
    assert result.nested_lists == [[1, 2], [3, 4]]


def test_old_style_with_none() -> None:
    """Test old-style Optional with None value."""
    data: dict[Any, Any] = {
        "name": "Bob",
        "age": None,
        "tags": [],
        "metadata": {},
        "nested_lists": [],
    }

    result = deserialize(OldStyleAnnotations, data)

    assert result.name == "Bob"
    assert result.age is None
    assert result.tags == []
    assert result.metadata == {}
    assert result.nested_lists == []


def test_new_style_annotations() -> None:
    """Test deserialization with new-style type annotations."""
    data = {
        "name": "Charlie",
        "age": 25,
        "tags": ["go", "typescript"],
        "metadata": {"points": 200, "rank": 3},
        "nested_lists": [[5, 6], [7, 8]],
    }

    result = deserialize(NewStyleAnnotations, data)

    assert result.name == "Charlie"
    assert result.age == 25
    assert result.tags == ["go", "typescript"]
    assert result.metadata == {"points": 200, "rank": 3}
    assert result.nested_lists == [[5, 6], [7, 8]]


def test_new_style_with_none() -> None:
    """Test new-style union with None value."""
    data: dict[Any, Any] = {
        "name": "Diana",
        "age": None,
        "tags": [],
        "metadata": {},
        "nested_lists": [],
    }

    result = deserialize(NewStyleAnnotations, data)

    assert result.name == "Diana"
    assert result.age is None
    assert result.tags == []
    assert result.nested_lists == []


def test_mixed_style_annotations() -> None:
    """Test that mixing old and new style annotations works."""
    data = {
        "name": "Eve",
        "count": 42,
        "items": ["item1", "item2"],
        "mapping": {"key1": 1, "key2": 2},
    }

    result = deserialize(MixedStyleAnnotations, data)

    assert result.name == "Eve"
    assert result.count == 42
    assert result.items == ["item1", "item2"]
    assert result.mapping == {"key1": 1, "key2": 2}


def test_mixed_style_with_none() -> None:
    """Test mixed style with None value."""
    data: dict[Any, Any] = {
        "name": "Frank",
        "count": None,
        "items": [],
        "mapping": {},
    }

    result = deserialize(MixedStyleAnnotations, data)

    assert result.name == "Frank"
    assert result.count is None
    assert result.items == []
    assert result.mapping == {}


def test_nested_old_style() -> None:
    """Test nested old-style annotations."""
    data = {
        "items": [
            {"a": 1, "b": None},
            {"c": 3, "d": 4},
        ],
        "matrix": [
            [1, 2, 3],
            [4, 5, 6],
        ],
    }

    result = deserialize(NestedOldStyle, data)

    assert result.items == [
        {"a": 1, "b": None},
        {"c": 3, "d": 4},
    ]
    assert result.matrix == [
        [1, 2, 3],
        [4, 5, 6],
    ]


def test_nested_new_style() -> None:
    """Test nested new-style annotations."""
    data = {
        "items": [
            {"a": 1, "b": None},
            {"c": 3, "d": 4},
        ],
        "matrix": [
            [1, 2, 3],
            [4, 5, 6],
        ],
    }

    result = deserialize(NestedNewStyle, data)

    assert result.items == [
        {"a": 1, "b": None},
        {"c": 3, "d": 4},
    ]
    assert result.matrix == [
        [1, 2, 3],
        [4, 5, 6],
    ]


class OldStyleListOfClasses:
    """Old-style annotation with list of classes."""

    items: List["SimpleItem"]


class NewStyleListOfClasses:
    """New-style annotation with list of classes."""

    items: list["SimpleItem"]


class SimpleItem:
    """Simple item for testing."""

    value: int


def test_old_style_list_of_classes() -> None:
    """Test old-style list of custom classes."""
    data = {
        "items": [
            {"value": 1},
            {"value": 2},
            {"value": 3},
        ]
    }

    result = deserialize(OldStyleListOfClasses, data)

    assert len(result.items) == 3
    assert all(isinstance(item, SimpleItem) for item in result.items)
    assert [item.value for item in result.items] == [1, 2, 3]


def test_new_style_list_of_classes() -> None:
    """Test new-style list of custom classes."""
    data = {
        "items": [
            {"value": 4},
            {"value": 5},
            {"value": 6},
        ]
    }

    result = deserialize(NewStyleListOfClasses, data)

    assert len(result.items) == 3
    assert all(isinstance(item, SimpleItem) for item in result.items)
    assert [item.value for item in result.items] == [4, 5, 6]


class OldStyleComplexUnions:
    """Old-style complex union types."""

    value: Optional[List[Dict[str, int]]]


class NewStyleComplexUnions:
    """New-style complex union types."""

    value: list[dict[str, int]] | None


def test_old_style_complex_union() -> None:
    """Test old-style complex union type."""
    data = {"value": [{"a": 1}, {"b": 2}]}
    result = deserialize(OldStyleComplexUnions, data)
    assert result.value == [{"a": 1}, {"b": 2}]

    data_none = {"value": None}
    result_none = deserialize(OldStyleComplexUnions, data_none)
    assert result_none.value is None


def test_new_style_complex_union() -> None:
    """Test new-style complex union type."""
    data = {"value": [{"a": 1}, {"b": 2}]}
    result = deserialize(NewStyleComplexUnions, data)
    assert result.value == [{"a": 1}, {"b": 2}]

    data_none = {"value": None}
    result_none = deserialize(NewStyleComplexUnions, data_none)
    assert result_none.value is None

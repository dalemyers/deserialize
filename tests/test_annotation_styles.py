"""Test that both old and new style type annotations work correctly."""

import os
import sys
from typing import Dict, List, Optional

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize

# pylint: enable=wrong-import-position


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


def test_old_style_annotations():
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


def test_old_style_with_none():
    """Test old-style Optional with None value."""
    data = {
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


def test_new_style_annotations():
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


def test_new_style_with_none():
    """Test new-style union with None value."""
    data = {
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


def test_mixed_style_annotations():
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


def test_mixed_style_with_none():
    """Test mixed style with None value."""
    data = {
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


def test_nested_old_style():
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


def test_nested_new_style():
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


def test_old_style_list_of_classes():
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


def test_new_style_list_of_classes():
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


def test_old_style_complex_union():
    """Test old-style complex union type."""
    data = {"value": [{"a": 1}, {"b": 2}]}
    result = deserialize(OldStyleComplexUnions, data)
    assert result.value == [{"a": 1}, {"b": 2}]

    data_none = {"value": None}
    result_none = deserialize(OldStyleComplexUnions, data_none)
    assert result_none.value is None


def test_new_style_complex_union():
    """Test new-style complex union type."""
    data = {"value": [{"a": 1}, {"b": 2}]}
    result = deserialize(NewStyleComplexUnions, data)
    assert result.value == [{"a": 1}, {"b": 2}]

    data_none = {"value": None}
    result_none = deserialize(NewStyleComplexUnions, data_none)
    assert result_none.value is None


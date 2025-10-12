"""Test metadata caching functionality."""

import os
import sys
import time
from typing import Dict, List, Optional, Union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, key, parser, default, auto_snake, ignore
from deserialize.metadata_cache import (
    get_class_metadata,
    clear_class_cache,
    FieldMetadata,
    ClassMetadata,
)

# pylint: enable=wrong-import-position


class SimpleClass:
    """Simple test class."""

    value: int
    name: str


@key("custom_id", "customId")
@parser("count", int)
@default("optional", "default_value")
class DecoratedClass:
    """Class with decorators."""

    custom_id: str
    count: int
    optional: str


@auto_snake()
class SnakeClass:
    """Class with auto_snake."""

    user_id: int
    user_name: str


class ParentClass:
    """Parent class for inheritance testing."""

    parent_field: str


class ChildClass(ParentClass):
    """Child class for inheritance testing."""

    child_field: int


def test_get_class_metadata_creates_cache() -> None:
    """Test that get_class_metadata creates and caches metadata."""
    # Clear any existing cache
    clear_class_cache(SimpleClass)

    # Should not have cache initially
    assert "__deserialize_cache__" not in SimpleClass.__dict__

    # Get metadata
    metadata = get_class_metadata(SimpleClass)

    # Should now have cache
    assert "__deserialize_cache__" in SimpleClass.__dict__
    assert isinstance(metadata, ClassMetadata)


def test_get_class_metadata_returns_cached() -> None:
    """Test that subsequent calls return cached metadata."""
    clear_class_cache(SimpleClass)

    # First call
    metadata1 = get_class_metadata(SimpleClass)

    # Second call should return same object
    metadata2 = get_class_metadata(SimpleClass)

    assert metadata1 is metadata2


def test_class_metadata_has_hints() -> None:
    """Test that ClassMetadata contains type hints."""
    metadata = get_class_metadata(SimpleClass)

    assert "value" in metadata.hints
    assert "name" in metadata.hints
    assert metadata.hints["value"] == int
    assert metadata.hints["name"] == str


def test_class_metadata_has_fields() -> None:
    """Test that ClassMetadata contains field metadata."""
    metadata = get_class_metadata(SimpleClass)

    assert "value" in metadata.fields
    assert "name" in metadata.fields
    assert isinstance(metadata.fields["value"], FieldMetadata)
    assert isinstance(metadata.fields["name"], FieldMetadata)


def test_field_metadata_basic_properties() -> None:
    """Test FieldMetadata basic properties."""
    metadata = get_class_metadata(SimpleClass)
    value_field = metadata.fields["value"]

    assert value_field.name == "value"
    assert value_field.type == int
    assert value_field.key == "value"
    assert value_field.ignore is False
    assert value_field.is_classvar is False


def test_field_metadata_decorator_info() -> None:
    """Test that FieldMetadata captures decorator information."""
    metadata = get_class_metadata(DecoratedClass)

    # Check key decorator
    assert metadata.fields["custom_id"].key == "customId"

    # Check parser decorator (function should be stored)
    assert metadata.fields["count"].parser is not None
    assert callable(metadata.fields["count"].parser)

    # Check default decorator
    assert metadata.fields["optional"].has_default is True
    assert metadata.fields["optional"].default_value == "default_value"


def test_field_metadata_type_classification() -> None:
    """Test that FieldMetadata pre-classifies types."""

    class TypeTestClass:
        """Class for testing type classification."""

        plain: int
        optional: Optional[str]
        union: Union[int, str]
        list_field: List[int]
        dict_field: Dict[str, int]

    metadata = get_class_metadata(TypeTestClass)

    # Plain type
    assert metadata.fields["plain"].is_union is False
    assert metadata.fields["plain"].is_list is False
    assert metadata.fields["plain"].is_dict is False

    # Optional (which is a Union)
    assert metadata.fields["optional"].is_union is True
    assert metadata.fields["optional"].union_types is not None

    # Union
    assert metadata.fields["union"].is_union is True
    assert metadata.fields["union"].union_types is not None

    # List
    assert metadata.fields["list_field"].is_list is True
    assert metadata.fields["list_field"].list_type == int

    # Dict
    assert metadata.fields["dict_field"].is_dict is True
    assert metadata.fields["dict_field"].dict_key_type == str
    assert metadata.fields["dict_field"].dict_value_type == int


def test_auto_snake_keys_precomputed() -> None:
    """Test that auto_snake keys are pre-computed."""
    metadata = get_class_metadata(SnakeClass)

    assert metadata.auto_snake is True

    # Check that camel and pascal keys are pre-computed
    user_id_field = metadata.fields["user_id"]
    assert user_id_field.camel_key is not None
    assert user_id_field.pascal_key is not None
    # The actual values
    assert user_id_field.camel_key == "userId"
    assert user_id_field.pascal_key == "UserId"


def test_cache_not_inherited() -> None:
    """Test that child classes don't inherit parent's cache."""
    clear_class_cache(ParentClass)
    clear_class_cache(ChildClass)

    # Create parent metadata
    parent_meta = get_class_metadata(ParentClass)

    # Parent should have cache
    assert "__deserialize_cache__" in ParentClass.__dict__

    # Child should NOT have cache yet (not inherited)
    assert "__deserialize_cache__" not in ChildClass.__dict__

    # Get child metadata
    child_meta = get_class_metadata(ChildClass)

    # Now child should have its own cache
    assert "__deserialize_cache__" in ChildClass.__dict__

    # They should be different objects
    assert parent_meta is not child_meta

    # Parent has only parent field
    assert "parent_field" in parent_meta.fields
    assert "child_field" not in parent_meta.fields

    # Child has both fields (due to type hint inheritance)
    assert "parent_field" in child_meta.fields
    assert "child_field" in child_meta.fields


def test_clear_class_cache() -> None:
    """Test that clear_class_cache removes cached metadata."""
    # Ensure cache exists
    get_class_metadata(SimpleClass)
    assert "__deserialize_cache__" in SimpleClass.__dict__

    # Clear it
    clear_class_cache(SimpleClass)

    # Should be gone
    assert "__deserialize_cache__" not in SimpleClass.__dict__


def test_metadata_cache_improves_performance() -> None:
    """Test that caching actually improves performance."""

    class PerfTestClass:
        """Class for performance testing."""

        field1: int
        field2: str
        field3: float
        field4: bool
        field5: List[int]

    # Clear cache
    clear_class_cache(PerfTestClass)

    # Time first call (creates cache)
    start1 = time.perf_counter()
    for _ in range(1000):
        get_class_metadata(PerfTestClass)
        clear_class_cache(PerfTestClass)
    time1 = time.perf_counter() - start1

    # Time with cache (should be faster)
    get_class_metadata(PerfTestClass)  # Create cache once
    start2 = time.perf_counter()
    for _ in range(1000):
        get_class_metadata(PerfTestClass)
    time2 = time.perf_counter() - start2

    # Cached version should be significantly faster
    # (At least 10x faster, usually 100x+)
    assert time2 < time1 / 10


def test_metadata_used_in_deserialization() -> None:
    """Test that metadata cache is actually used during deserialization."""

    @key("custom_field", "customField")
    class TestClass:
        """Test class."""

        custom_field: int

    # Clear cache
    clear_class_cache(TestClass)

    # Deserialize - should create cache
    data = {"customField": 42}
    result = deserialize(TestClass, data)

    assert result.custom_field == 42

    # Cache should exist now
    assert "__deserialize_cache__" in TestClass.__dict__

    # Deserialize again - should use cache
    result2 = deserialize(TestClass, data)
    assert result2.custom_field == 42


def test_immutable_types_handled() -> None:
    """Test that immutable types (like int) are handled gracefully."""
    # Should not raise an error even though we can't set attributes on int
    metadata = get_class_metadata(int)

    assert isinstance(metadata, ClassMetadata)
    # int won't have the cache attribute (immutable)
    assert "__deserialize_cache__" not in int.__dict__


def test_union_types_cached() -> None:
    """Test that union types are properly cached."""

    class UnionClass:
        """Class with union type."""

        value: Union[int, str, float]

    metadata = get_class_metadata(UnionClass)
    field = metadata.fields["value"]

    assert field.is_union is True
    assert field.union_types is not None
    assert len(field.union_types) == 3
    assert int in field.union_types
    assert str in field.union_types
    assert float in field.union_types


def test_ignore_decorator_cached() -> None:
    """Test that @ignore decorator information is cached."""

    @ignore("computed_field")
    class IgnoreTestClass:
        """Class with ignored field."""

        regular_field: int
        computed_field: str

    metadata = get_class_metadata(IgnoreTestClass)

    assert metadata.fields["regular_field"].ignore is False
    assert metadata.fields["computed_field"].ignore is True


def test_metadata_with_no_type_hints() -> None:
    """Test that classes with no type hints still create metadata."""

    class NoHintsClass:
        """Class without type hints."""

    metadata = get_class_metadata(NoHintsClass)

    assert isinstance(metadata, ClassMetadata)
    assert len(metadata.hints) == 0
    assert len(metadata.fields) == 0


def test_parser_function_cached() -> None:
    """Test that parser functions are cached and callable."""

    @parser("value", lambda x: int(x) * 2)
    class ParserTestClass:
        """Class with parser."""

        value: int

    metadata = get_class_metadata(ParserTestClass)
    field = metadata.fields["value"]

    assert field.parser is not None
    assert callable(field.parser)

    # Test the parser works
    assert field.parser(5) == 10
    assert field.parser("3") == 6

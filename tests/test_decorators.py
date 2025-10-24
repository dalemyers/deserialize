"""Test decorator functionality for deserialization."""

import datetime
import math
import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    DeserializeException,
    constructed,
    default,
    deserialize,
    ignore,
    key,
    parser,
)

# pylint: enable=wrong-import-position


# ============================================================================
# Key Decorator Tests
# ============================================================================


@key("field_1", "one")
@key("field_2", "two")
class KeySampleItem:
    """Sample item for use in tests."""

    field_1: int
    field_2: str


@key("identifier", "id")
class KeySecondaryItem:
    """Secondary sample item for use in tests."""

    identifier: int


def test_keys() -> None:
    """Test that key mapping works correctly."""
    data = {"one": 1, "two": "two"}

    instance_one = deserialize(KeySampleItem, data)
    assert data["one"] == instance_one.field_1
    assert data["two"] == instance_one.field_2

    instance_two = deserialize(KeySecondaryItem, {"id": 123})
    assert instance_two.identifier == 123


# ============================================================================
# Default Decorator Tests
# ============================================================================


@default("two", "two")
class DefaultSampleItem:
    """Sample item for use in tests."""

    one: int
    two: str


@default("two", "two")
class DefaultSampleOptionalItem:
    """Sample item for use in tests."""

    one: int
    two: str | None


def test_default() -> None:
    """Test that default values work correctly."""
    test_cases: list[dict[str, Any]] = [{"one": 1, "two": "two"}, {"one": 1}]

    for test_case in test_cases:
        instance = deserialize(DefaultSampleItem, test_case)
        assert test_case["one"] == instance.one
        assert instance.two == "two"

        optional_instance = deserialize(DefaultSampleOptionalItem, test_case)
        assert test_case["one"] == optional_instance.one
        assert optional_instance.two == "two"

    invalid_test_cases = [{"one": 1, "two": None}]

    for test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(DefaultSampleItem, test_case)


# ============================================================================
# Parser Decorator Tests
# ============================================================================


@parser("int_field", int)
@parser("datetime_field", datetime.datetime.fromtimestamp)
@parser("some_values", lambda x: [y * 2 for y in x])
class ParserSampleItem:
    """Sample item for use in tests."""

    int_field: int
    datetime_field: datetime.datetime
    some_values: list[int]


def test_parser() -> None:
    """Test that parsers are applied correctly."""
    instance = deserialize(
        ParserSampleItem,
        {"int_field": "1", "datetime_field": 1543770752, "some_values": [1, 2, 3]},
    )
    assert instance.int_field == 1
    assert instance.datetime_field == datetime.datetime(2018, 12, 2, 17, 12, 32)
    assert instance.some_values == [2, 4, 6]


# ============================================================================
# Ignore Decorator Tests
# ============================================================================


@ignore("field_2")
class IgnoreSampleItem:
    """Sample item for use in tests."""

    field_1: int
    field_2: int


def test_ignore() -> None:
    """Test that ignored fields are skipped."""
    data = {
        "field_1": 1,
    }

    instance = deserialize(IgnoreSampleItem, data)
    assert data["field_1"] == instance.field_1


# ============================================================================
# Constructed Decorator Tests
# ============================================================================


@constructed(lambda x: setattr(x, "constructed", True))
class ConstructedBasic:
    """Represents a basic class."""

    one: int


class ConstructedBasicUnconstructed:
    """Represents a basic class."""

    one: int


def convert_to_radians(instance: "PolarCoordinate") -> None:
    """Convert the angle on a PolarCoordinate from degrees to radians."""
    instance.angle = instance.angle * math.pi / 180


@constructed(convert_to_radians)
class PolarCoordinate:
    """Represents a polar coordinate."""

    angle: float
    magnitude: float


def test_constructed() -> None:
    """Test that the constructed decorator works correctly"""
    data = [{"one": 1}]

    for item in data:
        basic_instance = deserialize(ConstructedBasic, item)
        assert getattr(basic_instance, "constructed")
        unconstructed_instance = deserialize(ConstructedBasicUnconstructed, item)
        with pytest.raises(AttributeError):
            getattr(unconstructed_instance, "constructed")


def test_constructed_polar() -> None:
    """Test that the polar coordinates example from the README works."""
    data = {"angle": 180.0, "magnitude": 42.0}

    instance = deserialize(PolarCoordinate, data)

    assert -0.0001 < instance.angle - math.pi < 0.0001
    assert instance.magnitude == data["magnitude"]


# ============================================================================
# Decorator Combination Tests
# ============================================================================


def test_key_and_parser_together() -> None:
    """Test using @key and @parser decorators on the same field."""

    @key("int_value", "IntValue")
    @parser("IntValue", int)
    class Combined:
        """Class with both key and parser."""

        int_value: int

    data = {"IntValue": "42"}
    instance = deserialize(Combined, data)
    assert instance.int_value == 42


def test_key_and_default_together() -> None:
    """Test using @key and @default decorators on the same field."""

    @key("custom_field", "customField")
    @default("custom_field", 100)
    class Combined:
        """Class with both key and default."""

        custom_field: int

    # Test with value present
    data1 = {"customField": 50}
    instance1 = deserialize(Combined, data1)
    assert instance1.custom_field == 50

    # Test with value missing (should use default)
    data2: dict[str, int] = {}
    instance2 = deserialize(Combined, data2)
    assert instance2.custom_field == 100


def test_parser_and_default_together() -> None:
    """Test using @parser and @default decorators on the same field."""

    @parser("value", lambda x: x * 2)
    @default("value", 5)
    class Combined:
        """Class with both parser and default."""

        value: int

    # Test with value present (should be parsed)
    data1 = {"value": 10}
    instance1 = deserialize(Combined, data1)
    assert instance1.value == 20

    # Test with value missing (should use default, not parsed)
    data2: dict[str, int] = {}
    instance2 = deserialize(Combined, data2)
    assert instance2.value == 5


def test_multiple_keys_on_class() -> None:
    """Test multiple @key decorators on the same class."""

    @key("field_a", "fieldA")
    @key("field_b", "fieldB")
    @key("field_c", "fieldC")
    class MultiKey:
        """Class with multiple key mappings."""

        field_a: int
        field_b: str
        field_c: float

    data = {"fieldA": 1, "fieldB": "test", "fieldC": 3.14}
    instance = deserialize(MultiKey, data)

    assert instance.field_a == 1
    assert instance.field_b == "test"
    assert instance.field_c == 3.14


def test_multiple_defaults_on_class() -> None:
    """Test multiple @default decorators on the same class."""

    @default("field_a", 10)
    @default("field_b", "default")
    @default("field_c", 3.14)
    class MultiDefault:
        """Class with multiple defaults."""

        field_a: int
        field_b: str
        field_c: float

    # Test with all fields missing
    data1: dict[str, int] = {}
    instance1 = deserialize(MultiDefault, data1)
    assert instance1.field_a == 10
    assert instance1.field_b == "default"
    assert instance1.field_c == 3.14

    # Test with some fields present
    data2 = {"field_a": 99}
    instance2 = deserialize(MultiDefault, data2)
    assert instance2.field_a == 99
    assert instance2.field_b == "default"
    assert instance2.field_c == 3.14


def test_multiple_parsers_on_class() -> None:
    """Test multiple @parser decorators on the same class."""

    @parser("field_a", int)
    @parser("field_b", str.upper)
    @parser("field_c", lambda x: x * 2)
    class MultiParser:
        """Class with multiple parsers."""

        field_a: int
        field_b: str
        field_c: int

    data = {"field_a": "42", "field_b": "hello", "field_c": 5}
    instance = deserialize(MultiParser, data)

    assert instance.field_a == 42
    assert instance.field_b == "HELLO"
    assert instance.field_c == 10


def test_all_decorators_combined() -> None:
    """Test using all relevant decorators together."""

    @key("custom_name", "customName")
    @parser("customName", int)
    @default("optional_value", "default")
    @ignore("ignored_field")
    class AllDecorators:
        """Class with all decorators."""

        custom_name: int
        optional_value: str
        ignored_field: str

    # Test with all values
    data1 = {"customName": "123", "optional_value": "provided"}
    instance1 = deserialize(AllDecorators, data1)
    assert instance1.custom_name == 123
    assert instance1.optional_value == "provided"

    # Test with default used
    data2 = {"customName": "456"}
    instance2 = deserialize(AllDecorators, data2)
    assert instance2.custom_name == 456
    assert instance2.optional_value == "default"


def test_ignore_with_other_decorators() -> None:
    """Test that @ignore properly ignores fields even when other decorators are present."""

    @ignore("computed_field")
    @default("computed_field", 999)  # This should be ignored
    class IgnoreWithDefault:
        """Class with ignored field that has a default."""

        value: int
        computed_field: int

    data = {"value": 42}

    # The ignored field should not be set, even though it has a default
    instance = deserialize(IgnoreWithDefault, data)
    assert instance.value == 42
    # The computed_field won't be set by deserialize since it's ignored
    # This will raise AttributeError if accessed unless set elsewhere
    with pytest.raises(AttributeError):
        _ = instance.computed_field

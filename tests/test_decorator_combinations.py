"""Test multiple decorators and decorator combinations."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, key, parser, default, ignore

# pylint: enable=wrong-import-position


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

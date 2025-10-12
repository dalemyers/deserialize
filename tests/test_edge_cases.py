"""Test edge cases and corner scenarios."""

import os
import sys
from typing import Any, ClassVar, Union

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    deserialize,
    parser,
    default,
    constructed,
    auto_snake,
    DeserializeException,
)

# pylint: enable=wrong-import-position


def test_parser_with_none_optional() -> None:
    """Test parser behavior with None values in Optional fields."""

    def safe_parser(value):
        """Parser that handles None."""
        if value is None:
            return None
        return int(value)

    @parser("optional_int", safe_parser)
    class WithOptionalParser:
        """Class with parser on optional field."""

        optional_int: int | None

    # Test with None
    data1 = {"optional_int": None}
    instance1 = deserialize(WithOptionalParser, data1)
    assert instance1.optional_int is None

    # Test with value
    data2 = {"optional_int": "42"}
    instance2 = deserialize(WithOptionalParser, data2)
    assert instance2.optional_int == 42


def test_parser_with_none_non_optional() -> None:
    """Test parser that receives None for non-optional field should fail type check."""

    def bad_parser(value):
        """Parser that doesn't handle None properly."""
        return int(value)  # This will fail if value is None

    @parser("value", bad_parser)
    class WithBadParser:
        """Class with parser that doesn't handle None."""

        value: int

    data = {"value": None}

    # This should raise because None can't be int()'ed
    with pytest.raises((DeserializeException, TypeError, ValueError)):
        deserialize(WithBadParser, data)


def test_default_with_none_value() -> None:
    """Test that default value can be explicitly None."""

    @default("optional_field", None)
    class WithNoneDefault:
        """Class with None as default."""

        required_field: int
        optional_field: str | None

    data = {"required_field": 42}
    instance = deserialize(WithNoneDefault, data)

    assert instance.required_field == 42
    assert instance.optional_field is None


def test_constructed_with_exception() -> None:
    """Test @constructed decorator when the function raises an exception."""

    def failing_constructor(instance):
        """Constructor that always fails."""
        raise ValueError("Construction failed!")

    @constructed(failing_constructor)
    class FailingConstruction:
        """Class with failing constructed decorator."""

        value: int

    data = {"value": 42}

    with pytest.raises(ValueError) as exc_info:
        deserialize(FailingConstruction, data)

    assert "Construction failed!" in str(exc_info.value)


def test_constructed_with_modification() -> None:
    """Test @constructed decorator that modifies the instance."""

    def validate_and_modify(instance):
        """Validate and modify instance."""
        if instance.value < 0:
            raise ValueError("Value must be positive")
        instance.doubled = instance.value * 2

    @constructed(validate_and_modify)
    class WithValidation:
        """Class with validation in constructed."""

        value: int

    # Valid case
    data1 = {"value": 10}
    instance1 = deserialize(WithValidation, data1)
    assert instance1.value == 10
    assert instance1.doubled == 20

    # Invalid case
    data2 = {"value": -5}
    with pytest.raises(ValueError) as exc_info:
        deserialize(WithValidation, data2)
    assert "must be positive" in str(exc_info.value)


def test_parser_returns_wrong_type() -> None:
    """Test parser that returns incompatible type."""

    @parser("int_field", lambda x: "not_an_int")
    class WrongTypeParser:
        """Class with parser returning wrong type."""

        int_field: int

    data = {"int_field": 42}

    with pytest.raises(DeserializeException):
        deserialize(WrongTypeParser, data)


def test_dict_with_int_keys() -> None:
    """Test dictionary with integer keys."""

    class IntKeyDict:
        """Class with int-keyed dict."""

        data: dict[int, str]

    valid_data = {"data": {1: "one", 2: "two", 3: "three"}}
    instance = deserialize(IntKeyDict, valid_data)

    assert instance.data[1] == "one"
    assert instance.data[2] == "two"
    assert instance.data[3] == "three"


def test_dict_with_wrong_key_type() -> None:
    """Test dictionary with wrong key type fails."""

    class IntKeyDict:
        """Class with int-keyed dict."""

        data: dict[int, str]

    # String keys when int expected
    invalid_data = {"data": {"one": "1", "two": "2"}}

    with pytest.raises(DeserializeException):
        deserialize(IntKeyDict, invalid_data)


def test_nested_auto_snake() -> None:
    """Test auto_snake with nested objects."""

    @auto_snake()
    class InnerSnake:
        """Inner class with snake case."""

        inner_field: str
        inner_number: int

    @auto_snake()
    class OuterSnake:
        """Outer class with snake case."""

        outer_field: str
        nested_object: InnerSnake

    data = {
        "OuterField": "test",
        "NestedObject": {"InnerField": "nested", "InnerNumber": 42},
    }

    instance = deserialize(OuterSnake, data)
    assert instance.outer_field == "test"
    assert instance.nested_object.inner_field == "nested"
    assert instance.nested_object.inner_number == 42


def test_empty_list_typed() -> None:
    """Test empty list with type annotation."""

    class WithEmptyList:
        """Class with list field."""

        items: list[int]

    data: dict[str, list[int]] = {"items": []}
    instance = deserialize(WithEmptyList, data)

    assert instance.items == []
    assert isinstance(instance.items, list)


def test_empty_dict_typed() -> None:
    """Test empty dict with type annotation."""

    class WithEmptyDict:
        """Class with dict field."""

        mapping: dict[str, int]

    data: dict[str, dict[str, int]] = {"mapping": {}}
    instance = deserialize(WithEmptyDict, data)

    assert instance.mapping == {}
    assert isinstance(instance.mapping, dict)


def test_union_error_message_quality() -> None:
    """Test that union deserialization provides helpful error messages."""

    class UnionClass:
        """Class with union field."""

        value: Union[int, str]

    # This should fail because None is not in the union
    data = {"value": None}

    with pytest.raises(DeserializeException) as exc_info:
        deserialize(UnionClass, data)

    error_msg = str(exc_info.value)
    # Should mention the union type or show multiple attempts
    assert "union" in error_msg.lower() or "->" in error_msg


def test_any_type_accepts_everything() -> None:
    """Test that Any type accepts any value."""

    class WithAny:
        """Class with Any field."""

        anything: Any

    test_values: list[dict[str, Any]] = [
        {"anything": 42},
        {"anything": "string"},
        {"anything": [1, 2, 3]},
        {"anything": {"nested": "dict"}},
        {"anything": None},
        {"anything": 3.14},
    ]

    for data in test_values:
        instance = deserialize(WithAny, data)
        assert instance.anything == data["anything"]


def test_classvar_cannot_be_set() -> None:
    """Test that attempting to set a ClassVar raises an error."""

    class WithClassVar:
        """Class with ClassVar."""

        class_value: ClassVar[int] = 42
        instance_value: int

    # Data that tries to set the ClassVar
    data: dict[str, int] = {"class_value": 100, "instance_value": 1}

    with pytest.raises(DeserializeException) as exc_info:
        deserialize(WithClassVar, data)

    assert "ClassVar" in str(exc_info.value)

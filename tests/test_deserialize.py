"""Test deserializing."""

import os
import sys
from typing import Any, Dict, List, Optional, Union

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, DeserializeException

# pylint: enable=wrong-import-position


class UnannotatedClass:
    """Test class with no type annotations."""

    def __init__(self, value):
        self.value = value


class SinglePropertySimpleType:
    """Test class with a single property of a simple type."""

    my_property: int

    def __str__(self):
        return str({"my_property": self.my_property})


class MultiPropertySimpleType:
    """Test class with multiple properties of a simple type."""

    my_int_property: int
    my_str_property: str

    def __str__(self):
        return str(
            {
                "my_int_property": self.my_int_property,
                "my_str_property": self.my_str_property,
            }
        )


class SinglePropertyComplexType:
    """Test class with a single property of a complex type."""

    my_list: List[int]

    def __str__(self):
        return str([str(item) for item in self.my_list])


class ComplexNestedType:
    """Test class with complex nested information."""

    one: int
    two: Optional[str]
    three: SinglePropertySimpleType
    four: MultiPropertySimpleType
    five: Optional[SinglePropertySimpleType]
    six: List[SinglePropertyComplexType]

    def __str__(self):
        return str(
            {
                "one": self.one,
                "two": self.two,
                "three": str(self.three),
                "four": str(self.four),
                "five": str(self.five),
                "six": str([str(item) for item in self.six]),
            }
        )


class TypeWithSimpleDict:
    """Test a class that has a simple dict embedded."""

    value: int
    dict_value: dict


class TypeWithDict:
    """Test a class that has a dict embedded."""

    value: int
    dict_value: Dict[str, int]


class TypeWithComplexDict:
    """Test a class that has a complex dict embedded."""

    value: int
    dict_value: Dict[str, TypeWithDict]
    any_dict_value: Dict[str, Any]


class TypeWithUnion:
    """Test a class that has a Union embedded."""

    union_value: Union[str, int]


class NonJsonTypes:
    """Test a class that uses base types that aren't JSON compatible."""

    one: tuple
    two: range


def test_single_simple() -> None:
    """Test that items with a single property and simple types deserialize."""
    valid_test_cases = [
        {"my_property": 1},
        {"my_property": 234},
        {"my_property": -53},
    ]

    invalid_test_cases = [
        {"my_property": None},
        {"my_property": 3.14156},
        {"my_property": "Hello"},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(SinglePropertySimpleType, test_case)
        assert test_case["my_property"] == instance.my_property

    for invalid_test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(SinglePropertySimpleType, invalid_test_case)


def test_multi_simple() -> None:
    """Test that items with multiple properties and simple types deserialize."""
    valid_test_cases = [
        {"my_int_property": 1, "my_str_property": "Hello"},
        {"my_int_property": 234, "my_str_property": "this"},
        {"my_int_property": -53, "my_str_property": "is"},
        {"my_int_property": 0, "my_str_property": "a"},
        {"my_int_property": 99999999999, "my_str_property": "test"},
    ]

    invalid_test_cases = [
        {"my_int_property": None, "my_str_property": "Test"},
        {"my_int_property": 3.14156, "my_str_property": "Test"},
        {"my_int_property": "Hello", "my_str_property": "Test"},
        {"my_int_property": 12, "my_str_property": None},
        {"my_int_property": 34, "my_str_property": 42},
        {"my_int_property": 56, "my_str_property": ["Test"]},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(MultiPropertySimpleType, test_case)
        assert test_case["my_int_property"] == instance.my_int_property
        assert test_case["my_str_property"] == instance.my_str_property

    for invalid_test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(MultiPropertySimpleType, invalid_test_case)


def test_single_complex() -> None:
    """Test that items with a single property and complex types deserialize."""
    valid_test_cases: list[dict[str, list[int]]] = [
        {"my_list": []},
        {"my_list": [1, 2, 3]},
        {"my_list": [2, -4, 23]},
    ]

    invalid_test_cases: list[dict[str, Any]] = [
        {"my_list": [None]},
        {"my_list": [1, None, 3]},
        {"my_list": [2, 3.14, 23]},
        {"my_list": [2, 3, "Hello"]},
        {"my_list": 2},
        {"my_list": (2, 3, 4)},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(SinglePropertyComplexType, test_case)
        assert test_case["my_list"] == instance.my_list

    for invalid_test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(SinglePropertyComplexType, invalid_test_case)


def test_complex_nested() -> None:
    """Test that items in a complex nested object deserialize."""
    valid_test_cases: list[dict[str, Any]] = [
        {
            "one": 1,
            "two": "2",
            "three": {"my_property": 3},
            "four": {"my_int_property": 34, "my_str_property": "Hello"},
            "five": {"my_property": 3},
            "six": [
                {"my_list": []},
                {"my_list": [1, 2, 3]},
                {"my_list": [2, -4, 23]},
            ],
        },
        {
            "one": 12312312,
            "two": None,
            "three": {"my_property": 3},
            "four": {"my_int_property": 34, "my_str_property": "Hello"},
            "five": None,
            "six": [
                {"my_list": []},
                {"my_list": [1, 2, 3]},
                {"my_list": [2, -4, 23]},
            ],
        },
    ]

    invalid_test_cases: list[dict[str, Any]] = [
        {
            "one": None,
            "two": "2",
            "three": {"my_property": 3},
            "four": {"my_int_property": 34, "my_str_property": "Hello"},
            "five": {"my_property": 3},
            "six": [
                {"my_list": []},
                {"my_list": [1, 2, 3]},
                {"my_list": [2, -4, 23]},
            ],
        },
        {
            "one": 12312312,
            "two": None,
            "three": {"my_property": 3},
            "four": {"my_int_property": 34, "my_str_property": "Hello"},
            "five": None,
            "six": [
                {"my_list": []},
                {"my_list": [1, "Test", 3]},
                {"my_list": [2, -4, 23]},
            ],
        },
    ]

    for test_case in valid_test_cases:
        instance = deserialize(ComplexNestedType, test_case)
        assert test_case["one"] == instance.one
        assert test_case["two"] == instance.two
        assert test_case["three"]["my_property"] == instance.three.my_property
        assert test_case["four"]["my_int_property"] == instance.four.my_int_property
        assert test_case["four"]["my_str_property"] == instance.four.my_str_property
        if test_case["five"] is None:
            assert instance.five is None
        else:
            assert test_case["five"]["my_property"] == instance.five.my_property
        for i in range(0, len(test_case["six"])):
            assert test_case["six"][i]["my_list"] == instance.six[i].my_list

    for test_case in invalid_test_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(ComplexNestedType, test_case)


def test_unannotated() -> None:
    """Test parsing unannotated classes."""
    data = {"value": 1}

    with pytest.raises(DeserializeException):
        _ = deserialize(UnannotatedClass, data)


def test_type_with_dict() -> None:
    """Test parsing types with dicts."""

    test_cases: list[dict[str, Any]] = [
        {"value": 1, "dict_value": {"Hello": 1, "World": 2}},
        {"value": 1, "dict_value": {}},
    ]

    for test_case in test_cases:
        instance = deserialize(TypeWithDict, test_case)
        assert instance.value == test_case["value"]
        for key, value in test_case["dict_value"].items():
            assert instance.dict_value.get(key) == value

    failure_cases: list[dict[str, Any]] = [
        {"value": 1, "dict_value": {"Hello": "one", "World": "two"}},
        {"value": 1, "dict_value": {1: "one", 2: "two"}},
        {"value": 1, "dict_value": []},
    ]

    for test_case in failure_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(TypeWithDict, test_case)


def test_type_with_simple_dict() -> None:
    """Test parsing types with dicts."""

    test_cases: list[dict[str, Any]] = [
        {"value": 1, "dict_value": {"Hello": 1, "World": 2}},
        {"value": 1, "dict_value": {}},
    ]

    for test_case in test_cases:
        instance = deserialize(TypeWithSimpleDict, test_case)
        assert instance.value == test_case["value"]
        for key, value in test_case["dict_value"].items():
            assert instance.dict_value.get(key) == value

    failure_cases: list[dict[str, Any]] = [
        {"value": 1, "dict_value": []},
    ]

    for test_case in failure_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(TypeWithDict, test_case)


def test_type_with_complex_dict() -> None:
    """Test parsing types with complex dicts."""

    test_cases: list[dict[str, Any]] = [
        {
            "value": 1,
            "dict_value": {"Hello": {"value": 1, "dict_value": {"Hello": 1, "World": 2}}},
            "any_dict_value": {"Hello": 4, "World": ":D"},
        },
    ]

    for test_case in test_cases:
        instance = deserialize(TypeWithComplexDict, test_case)
        assert instance.value == test_case["value"]
        sub_instance = instance.dict_value["Hello"]
        sub_test_case = test_case["dict_value"]["Hello"]
        assert sub_instance.value == sub_test_case["value"]
        for key, value in sub_test_case["dict_value"].items():
            assert sub_instance.dict_value.get(key) == value

    failure_cases: list[dict[str, Any]] = [
        {"value": 1, "dict_value": {"Hello": {}}},
        {
            "value": 1,
            "dict_value": {"Hello": {"value": 1, "dict_value": {"Hello": "one", "World": 2}}},
        },
        {"value": 1, "dict_value": {"Hello": {"value": 1}}},
    ]

    for test_case in failure_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(TypeWithComplexDict, test_case)


def test_type_with_union() -> None:
    """Test parsing types with complex dicts."""

    test_cases: list[dict[str, Any]] = [
        {"union_value": "one"},
        {"union_value": 1},
    ]

    for test_case in test_cases:
        instance = deserialize(TypeWithUnion, test_case)
        assert instance.union_value == test_case["union_value"]

    failure_cases = [
        {"union_value": None},
    ]

    for test_case in failure_cases:
        with pytest.raises(DeserializeException):
            _ = deserialize(TypeWithUnion, test_case)


def test_non_json_types() -> None:
    """Test parsing types that are not JSON compatible."""

    data = {"one": (1, 2), "two": range(3)}

    result = deserialize(NonJsonTypes, data)
    assert data["one"] == result.one
    assert data["two"] == result.two

"""Test deserializing."""

import os
import re
import sys
from typing import Callable, Dict, List, Optional, Pattern, Tuple, Union
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position


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
        return str({
            "my_int_property": self.my_int_property,
            "my_str_property": self.my_str_property
        })


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
        return str({
            "one": self.one,
            "two": self.two,
            "three": str(self.three),
            "four": str(self.four),
            "five": str(self.five),
            "six": str([str(item) for item in self.six])
        })


class TypeWithDict:
    """Test a class that has a dict embedded."""
    value: int
    dict_value: Dict[str, int]


class TypeWithComplexDict:
    """Test a class that has a complex dict embedded."""
    value: int
    dict_value: Dict[str, TypeWithDict]


class TypeWithEllipseTuple:
    """Test a class that has a Tuple embedded."""
    tuple_value: Tuple[str, ...]


class NonJsonTypes:
    """Test a class that uses base types that aren't JSON compatible."""
    one: tuple
    two: range


class DeserializationTestSuite(unittest.TestCase):
    """Deserialization test cases."""

    def test_single_simple(self):
        """Test that items with a single property and simple types deserialize."""
        valid_test_cases = [
            {"my_property": 1},
            {"my_property": 234},
            {"my_property": -53},
        ]

        invalid_test_cases = [
            {"my_property": None},
            {"my_property": 3.14156},
            {"my_property": "Hello"}
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(SinglePropertySimpleType, test_case)
            self.assertEqual(test_case["my_property"], instance.my_property)

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(SinglePropertySimpleType, test_case)

    def test_multi_simple(self):
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
            instance = deserialize.deserialize(MultiPropertySimpleType, test_case)
            self.assertEqual(test_case["my_int_property"], instance.my_int_property)
            self.assertEqual(test_case["my_str_property"], instance.my_str_property)

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(MultiPropertySimpleType, test_case)

    def test_single_complex(self):
        """Test that items with a single property and complex types deserialize."""
        valid_test_cases = [
            {"my_list": []},
            {"my_list": [1, 2, 3]},
            {"my_list": [2, -4, 23]},
        ]

        invalid_test_cases = [
            {"my_list": [None]},
            {"my_list": [1, None, 3]},
            {"my_list": [2, 3.14, 23]},
            {"my_list": [2, 3, "Hello"]},
            {"my_list": 2},
            {"my_list": (2, 3, 4)},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(SinglePropertyComplexType, test_case)
            self.assertEqual(test_case["my_list"], instance.my_list)

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(SinglePropertyComplexType, test_case)

    def test_complex_nested(self):
        """Test that items in a complex nested object deserialize."""
        valid_test_cases = [
            {
                "one": 1,
                "two": "2",
                "three": {"my_property": 3},
                "four": {
                    "my_int_property": 34,
                    "my_str_property": "Hello"
                },
                "five": {"my_property": 3},
                "six": [
                    {"my_list": []},
                    {"my_list": [1, 2, 3]},
                    {"my_list": [2, -4, 23]},
                ]
            },
            {
                "one": 12312312,
                "two": None,
                "three": {"my_property": 3},
                "four": {
                    "my_int_property": 34,
                    "my_str_property": "Hello"
                },
                "five": None,
                "six": [
                    {"my_list": []},
                    {"my_list": [1, 2, 3]},
                    {"my_list": [2, -4, 23]},
                ]
            },
        ]

        invalid_test_cases = [
            {
                "one": None,
                "two": "2",
                "three": {"my_property": 3},
                "four": {
                    "my_int_property": 34,
                    "my_str_property": "Hello"
                },
                "five": {"my_property": 3},
                "six": [
                    {"my_list": []},
                    {"my_list": [1, 2, 3]},
                    {"my_list": [2, -4, 23]},
                ]
            },
            {
                "one": 12312312,
                "two": None,
                "three": {"my_property": 3},
                "four": {
                    "my_int_property": 34,
                    "my_str_property": "Hello"
                },
                "five": None,
                "six": [
                    {"my_list": []},
                    {"my_list": [1, "Test", 3]},
                    {"my_list": [2, -4, 23]},
                ]
            },
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(ComplexNestedType, test_case)
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case["two"], instance.two)
            self.assertEqual(test_case["three"]["my_property"], instance.three.my_property)
            self.assertEqual(test_case["four"]["my_int_property"], instance.four.my_int_property)
            self.assertEqual(test_case["four"]["my_str_property"], instance.four.my_str_property)
            if test_case["five"] is None:
                self.assertIsNone(instance.five)
            else:
                self.assertEqual(test_case["five"]["my_property"], instance.five.my_property)
            for i in range(0, len(test_case["six"])):
                self.assertEqual(test_case["six"][i]["my_list"], instance.six[i].my_list)

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(ComplexNestedType, test_case)

    def test_unannotated(self):
        """Test parsing unannotated classes."""
        data = {
            "value": 1
        }

        with self.assertRaises(deserialize.DeserializeException):
            _ = deserialize.deserialize(UnannotatedClass, data)

    def test_type_with_dict(self):
        """Test parsing types with dicts."""

        test_cases = [
            {
                "value": 1,
                "dict_value": {
                    "Hello": 1,
                    "World": 2
                }
            },
            {
                "value": 1,
                "dict_value": {}
            },
        ]

        for test_case in test_cases:
            instance = deserialize.deserialize(TypeWithDict, test_case)
            self.assertEqual(instance.value, test_case["value"])
            for key, value in test_case["dict_value"].items():
                self.assertEqual(instance.dict_value.get(key), value)

        failure_cases = [
            {
                "value": 1,
                "dict_value": {
                    "Hello": "one",
                    "World": "two"
                }
            },
            {
                "value": 1,
                "dict_value": {
                    1: "one",
                    2: "two"
                }
            },
            {
                "value": 1,
                "dict_value": []
            },
        ]

        for test_case in failure_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(TypeWithDict, test_case)

    def test_type_with_complex_dict(self):
        """Test parsing types with complex dicts."""

        test_cases = [
            {
                "value": 1,
                "dict_value": {
                    "Hello": {
                        "value": 1,
                        "dict_value": {
                            "Hello": 1,
                            "World": 2
                        }
                    }
                }
            },
        ]

        for test_case in test_cases:
            instance = deserialize.deserialize(TypeWithComplexDict, test_case)
            self.assertEqual(instance.value, test_case["value"])
            sub_instance = instance.dict_value["Hello"]
            sub_test_case = test_case["dict_value"]["Hello"]
            self.assertEqual(sub_instance.value, sub_test_case["value"])
            for key, value in sub_test_case["dict_value"].items():
                self.assertEqual(sub_instance.dict_value.get(key), value)

        failure_cases = [
            {
                "value": 1,
                "dict_value": {
                    "Hello": {}
                }
            },
            {
                "value": 1,
                "dict_value": {
                    "Hello": {
                        "value": 1,
                        "dict_value": {
                            "Hello": "one",
                            "World": 2
                        }
                    }
                }
            },
            {
                "value": 1,
                "dict_value": {
                    "Hello": {
                        "value": 1
                    }
                }
            },
        ]

        for test_case in failure_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(TypeWithComplexDict, test_case)

    def test_type_with_ellipse_tuple(self):
        """Test parsing types with complex dicts."""

        test_cases = [
            {
                "tuple_value": tuple()
            },
            {
                "tuple_value": ("one",)
            },
            {
                "tuple_value": ("one", "two", "three", "four")
            },
        ]

        for test_case in test_cases:
            instance = deserialize.deserialize(TypeWithEllipseTuple, test_case)
            self.assertEqual(instance.tuple_value, test_case["tuple_value"])

        failure_cases = [
            {
                "tuple_value": (1,)
            },
            {
                "tuple_value": ("one", 2)
            },
        ]

        for test_case in failure_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(TypeWithEllipseTuple, test_case)

    def test_non_json_types(self):
        """Test parsing types that are not JSON compatible."""

        data = {
            "one": (1,2),
            "two": range(3)
        }

        result = deserialize.deserialize(NonJsonTypes, data)
        self.assertEqual(data["one"], result.one)
        self.assertEqual(data["two"], result.two)

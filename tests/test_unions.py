"""Test deserializing tuples."""

import os
import sys
from typing import Optional, Union
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class BasicUnionClass:
    """Basic union example."""

    one: Union[str, int]


class SomeUnionClass:
    """Union example."""

    one: Union[str, int]
    two: Union[int, str]
    three: Union[int, Optional[str]]


class UnionTestSuite(unittest.TestCase):
    """Deserialization of union test cases."""

    def test_union_simple(self):
        """Test that items with a simple union property deserializes."""
        valid_test_cases = [
            {"one": 1},
            {"one": "1"},
        ]

        invalid_test_cases = [
            {"one": 3.1415},
            {"one": None},
            {"one": BasicUnionClass()},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(BasicUnionClass, test_case)
            self.assertEqual(test_case["one"], instance.one)

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(BasicUnionClass, test_case)

    def test_union(self):
        """Test that items with union properties deserializes."""

        valid_test_cases = [
            {"one": 1, "two": 2, "three": 3},
            {"one": 1, "two": "2", "three": 3},
            {"one": "1", "two": 2, "three": 3},
            {"one": "1", "two": "2", "three": 3},
            {"one": 1, "two": 2, "three": None},
            {"one": 1, "two": "2", "three": None},
            {"one": "1", "two": 2, "three": None},
            {"one": "1", "two": "2", "three": None},
            {"one": 1, "two": 2, "three": "3"},
            {"one": 1, "two": "2", "three": "3"},
            {"one": "1", "two": 2, "three": "3"},
            {"one": "1", "two": "2", "three": "3"},
        ]

        invalid_test_cases = [
            {"one": None, "two": 2, "three": 3},
            {"one": 1, "two": None, "three": 3},
            {"one": 1, "two": 2, "three": BasicUnionClass()},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(SomeUnionClass, test_case)
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case["two"], instance.two)
            self.assertEqual(test_case["three"], instance.three)

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(SomeUnionClass, test_case)
"""Test deserializing with specified constructors."""

import os
import sys
from typing import Optional
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class BasicConstructor:
    """Basic constructor example."""

    one: int
    two: int
    three: Optional[int]

    def __init__(self, one: int, two: int) -> None:
        self.one = one
        self.two = two
        self.three = None


class InheritedConstructor(BasicConstructor):
    """Inherited constructor example."""

    four: int


class ConstructorTestSuite(unittest.TestCase):
    """Deserialization of union test cases."""

    def test_basic_constructor(self):
        """Test that items with a constructor can be deserialized."""
        test_cases = [
            {"one": 1, "two": 2},
            {"one": 1, "two": 2, "three": None},
            {"one": 1, "two": 2, "three": 3},
        ]

        for test_case in test_cases:
            instance = deserialize.deserialize(BasicConstructor, test_case)
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case["two"], instance.two)
            self.assertEqual(test_case.get("three"), instance.three)

    def test_inherited_constructor(self):
        """Test that items with an inherited constructor can be deserialized."""
        test_cases = [
            {"one": 1, "two": 2, "four": 4},
            {"one": 1, "two": 2, "three": None, "four": 4},
            {"one": 1, "two": 2, "three": 3, "four": 4},
        ]

        for test_case in test_cases:
            instance = deserialize.deserialize(InheritedConstructor, test_case)
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case["two"], instance.two)
            self.assertEqual(test_case.get("three"), instance.three)
            self.assertEqual(test_case["four"], instance.four)

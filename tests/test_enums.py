"""Test deserializing enums."""

import enum
import os
import sys
from typing import Optional
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class SomeStringEnum(enum.Enum):
    """Enum example."""

    one = "One"
    two = "Two"
    three = "Three"


class SomeIntEnum(enum.Enum):
    """Enum example."""

    one = 1
    two = 2
    three = 3


class SomeClass:
    """Simple enum test class."""

    my_value: int
    my_enum: SomeStringEnum
    my_optional_enum: Optional[SomeIntEnum]


class EnumTestSuite(unittest.TestCase):
    """Deserialization of enum test cases."""

    def test_enums_simple(self):
        """Test that items with an enum property deserializes."""
        valid_test_cases = [
            {"my_value": 1, "my_enum": "One", "my_optional_enum": 1},
            {"my_value": 2, "my_enum": "Two", "my_optional_enum": 2},
            {"my_value": 3, "my_enum": "Three", "my_optional_enum": None},
        ]

        invalid_test_cases = [
            {"my_value": 1, "my_enum": None, "my_optional_enum": 1},
            {"my_value": 2, "my_enum": "two", "my_optional_enum": None},
            {"my_value": 3, "my_enum": 3, "my_optional_enum": "Three"},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(SomeClass, test_case)

            self.assertEqual(test_case["my_value"], instance.my_value)

            if test_case["my_enum"] is None:
                self.assertIsNone(instance.my_enum)
            else:
                self.assertEqual(test_case["my_enum"], instance.my_enum.value)

            if test_case["my_optional_enum"] is None:
                self.assertIsNone(instance.my_optional_enum)
            else:
                self.assertEqual(
                    test_case["my_optional_enum"], instance.my_optional_enum.value
                )

        for test_case in invalid_test_cases:
            with self.assertRaises(deserialize.DeserializeException):
                _ = deserialize.deserialize(SomeClass, test_case)

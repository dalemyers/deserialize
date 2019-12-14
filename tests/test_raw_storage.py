"""Test deserializing with raw storage."""

import os
import sys
from typing import List
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class SimpleStorageClass:
    """Basic storage example."""

    one: int


class BiggerStorageClass:
    """A more complex storage example."""

    one: int
    two: SimpleStorageClass
    three: List[str]


class RawStoreTestSuite(unittest.TestCase):
    """Test cases for raw storage."""

    def test_root_simple(self):
        """Test that root only storage works."""
        valid_test_cases = [
            {"one": 1},
            {"one": 3},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(
                SimpleStorageClass, test_case, raw_storage_mode=deserialize.RawStorageMode.root
            )
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case, instance.__deserialize_raw__)

    def test_root_bigger(self):
        """Test that root only storage works on more complex examples."""
        valid_test_cases = [
            {"one": 1, "two": {"one": 1}, "three": ["one", "two", "three"]},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(
                BiggerStorageClass, test_case, raw_storage_mode=deserialize.RawStorageMode.root
            )
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case["two"]["one"], instance.two.one)
            self.assertEqual(test_case["three"], instance.three)
            self.assertEqual(test_case, instance.__deserialize_raw__)
            self.assertFalse(hasattr(instance.two, "__deserialize_raw__"))

    def test_all_simple(self):
        """Test that all property storage works."""
        valid_test_cases = [
            {"one": 1},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(
                SimpleStorageClass, test_case, raw_storage_mode=deserialize.RawStorageMode.all
            )
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case, instance.__deserialize_raw__)

    def test_all_bigger(self):
        """Test that root only storage works on more complex examples."""
        valid_test_cases = [
            {"one": 1, "two": {"one": 1}, "three": ["one", "two", "three"]},
        ]

        for test_case in valid_test_cases:
            instance = deserialize.deserialize(
                BiggerStorageClass, test_case, raw_storage_mode=deserialize.RawStorageMode.all
            )
            self.assertEqual(test_case["one"], instance.one)
            self.assertEqual(test_case["two"]["one"], instance.two.one)
            self.assertEqual(test_case["three"], instance.three)
            self.assertEqual(test_case, instance.__deserialize_raw__)
            self.assertEqual(test_case["two"], instance.two.__deserialize_raw__)

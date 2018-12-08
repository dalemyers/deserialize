"""Test base types."""

import os
import sys
from typing import List
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position


class Item:
    """Sample item for use in tests."""
    field: int


class DeserializationBaseTypesTestSuite(unittest.TestCase):
    """Deserialization base types test cases."""

    def test_dicts(self):
        """Test that root dicts deserialize correctly."""

        data = {
            "field": 1
        }

        instance = deserialize.deserialize(Item, data)
        self.assertEqual(data["field"], instance.field)

    def test_lists(self):
        """Test that root lists deserialize correctly."""

        data = [
            {
                "field": 1
            }
        ]

        instances = deserialize.deserialize(List[Item], data)

        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0].field, data[0]["field"])

    def test_list_of_lists(self):
        """Test that root lists deserialize correctly."""

        data = [
            [
                {
                    "field": 1
                }
            ]
        ]

        instances = deserialize.deserialize(List[List[Item]], data)

        self.assertEqual(len(instances), 1)
        self.assertEqual(len(instances[0]), 1)
        self.assertEqual(instances[0][0].field, data[0][0]["field"])

    def test_invalid_lists(self):
        """Test that lists of base types don't parse."""

        data = [1, 2, 3]

        with self.assertRaises(deserialize.InvalidBaseTypeException):
            _ = deserialize.deserialize(List[int], data)

    def test_base_type(self):
        """Test that base types don't parse."""

        data = 1

        with self.assertRaises(deserialize.InvalidBaseTypeException):
            _ = deserialize.deserialize(int, data)

"""Test base types."""

import datetime
import os
import sys
from typing import Callable, List, Optional
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class Item:
    """Sample item for use in tests."""

    field: int


class Empty:
    """Sample empty item"""


class DeserializationBaseTypesTestSuite(unittest.TestCase):
    """Deserialization base types test cases."""

    def test_dicts(self):
        """Test that root dicts deserialize correctly."""

        data = {"field": 1}

        instance = deserialize.deserialize(Item, data)
        self.assertEqual(data["field"], instance.field)

    def test_empty_classes(self):
        """Test that empty classes throw an exception on deserialization."""

        data = {}

        with self.assertRaises(deserialize.DeserializeException):
            _ = deserialize.deserialize(Empty, data)

    def test_lists(self):
        """Test that root lists deserialize correctly."""

        data = [{"field": 1}]

        instances = deserialize.deserialize(List[Item], data)

        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0].field, data[0]["field"])

    def test_list_of_lists(self):
        """Test that root lists deserialize correctly."""

        data = [[{"field": 1}]]

        instances = deserialize.deserialize(List[List[Item]], data)

        self.assertEqual(len(instances), 1)
        self.assertEqual(len(instances[0]), 1)
        self.assertEqual(instances[0][0].field, data[0][0]["field"])

    def test_list_of_optionals(self):
        """Test that root lists deserialize correctly."""

        data = [1, None, 3, None, 5, None]

        instances = deserialize.deserialize(List[Optional[int]], data)

        self.assertEqual(instances, data)

    def test_base_type_lists(self):
        """Test that lists of base types parse."""

        data = [1, 2, 3]

        parsed = deserialize.deserialize(List[int], data)
        self.assertEqual(data, parsed)

    def test_base_type(self):
        """Test that base types don't parse."""

        base_types = [
            (1, int),
            ("Hello", str),
            (lambda x: x * 2, Callable),
            (3.14159, float),
            (datetime.datetime.now(), datetime.datetime),
            (set([]), set),
            ((1, 2), tuple),
            (range(3), range),
        ]

        for base_value, base_type in base_types:
            with self.assertRaises(deserialize.InvalidBaseTypeException):
                _ = deserialize.deserialize(base_type, base_value)

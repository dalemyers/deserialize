"""Test deserializing."""

import os
import sys
from typing import List
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position


class SampleItem:
    """Sample item for use in tests."""
    field_1: int
    field_2: str


class DeserializationAlternativesTestSuite(unittest.TestCase):
    """Deserialization example test cases."""

    def test_lists(self):
        """Test that root lists deserialize correctly."""

        data = [
            {
                "field_1": 1,
                "field_2": "two"
            }
        ]

        with self.assertRaises(deserialize.DeserializeException):
            _ = deserialize.deserialize(List[SampleItem], data)

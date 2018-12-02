"""Test deserializing."""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position


@deserialize.parser("int_field", int)
@deserialize.parser("datetime_field", datetime.datetime.fromtimestamp)
class SampleItem:
    """Sample item for use in tests."""
    int_field: int
    datetime_field: datetime.datetime


class DeserializationParserTestSuite(unittest.TestCase):
    """Deserialization parser test cases."""

    def test_parser(self):
        """Test that parsers are applied correctly."""

        instance = deserialize.deserialize(SampleItem, {"int_field": "1", "datetime_field": 1543770752})
        self.assertEqual(instance.int_field, 1)
        self.assertEqual(instance.datetime_field, datetime.datetime(2018, 12, 2, 17, 12, 32))

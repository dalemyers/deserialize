"""Test deserializing."""

import os
import sys
import typing
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position


class SampleItem1:
    """Sample item for use in tests."""
    field_1: typing.Union[int, str]


class DeserializationUnionTestSuite(unittest.TestCase):
    """Deserialization Union test cases."""

    def test_union_int(self):
        """Test that Union deserialize correctly as int."""

        data = {
            "field_1": 1,
        }

        instance = deserialize.deserialize(SampleItem1, data)
        self.assertEqual(data["field_1"], instance.field_1)
        self.assertIsInstance(instance.field_1, type(data["field_1"]))

    def test_union_str(self):
        """Test that Union deserialize correctly as str."""

        data = {
            "field_1": "1",
        }

        instance = deserialize.deserialize(SampleItem1, data)
        self.assertEqual(data["field_1"], instance.field_1)
        self.assertIsInstance(instance.field_1, type(data["field_1"]))

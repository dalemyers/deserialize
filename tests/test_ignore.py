"""Test deserializing."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


@deserialize.ignore("field_2")
class SampleItem:
    """Sample item for use in tests."""

    field_1: int
    field_2: int


class DeserializationInogreTestSuite(unittest.TestCase):
    """Deserialization ignore test cases."""

    def test_keys(self):
        """Test that root lists deserialize correctly."""

        data = {
            "field_1": 1,
        }

        instance = deserialize.deserialize(SampleItem, data)
        self.assertEqual(data["field_1"], instance.field_1)

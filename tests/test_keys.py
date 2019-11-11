"""Test deserializing."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


@deserialize.key("field_1", "one")
@deserialize.key("field_2", "two")
class SampleItem:
    """Sample item for use in tests."""

    field_1: int
    field_2: str


@deserialize.key("identifier", "id")
class SecondaryItem:
    """Secondary sample item for use in tests."""

    identifier: int


class DeserializationKeysTestSuite(unittest.TestCase):
    """Deserialization keyse test cases."""

    def test_keys(self):
        """Test that root lists deserialize correctly."""

        data = {"one": 1, "two": "two"}

        instance = deserialize.deserialize(SampleItem, data)
        self.assertEqual(data["one"], instance.field_1)
        self.assertEqual(data["two"], instance.field_2)

        instance = deserialize.deserialize(SecondaryItem, {"id": 123})
        self.assertEqual(instance.identifier, 123)

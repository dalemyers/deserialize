"""Test deserializing."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class Basic:
    """Represents a basic class."""

    one: int
    two: int


class DeserializationUnhandledTestSuite(unittest.TestCase):
    """Deserialization unhandled test cases."""

    def test_unhandled(self):
        """Test that rectange deserialization works correctly"""

        data = [{"one": 1, "two": 2, "three": 4, "four": 4}]

        for item in data:
            with self.assertRaises(deserialize.exceptions.UnhandledFieldException):
                deserialize.deserialize(Basic, item, throw_on_unhandled=True)

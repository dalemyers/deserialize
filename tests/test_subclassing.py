"""Test deserializing."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class Shape:
    """Represents a shape."""

    edges: int
    vertices: int


class Rectangle(Shape):
    """Represents a rectangle."""

    short_length: int
    long_length: int


class DeserializationSubclassingTestSuite(unittest.TestCase):
    """Deserialization subclassing test cases."""

    def test_rectangle(self):
        """Test that rectange deserialization works correctly"""

        shape_data = [
            {"edges": 4, "vertices": 4, "short_length": 4, "long_length": 6},
            {"edges": 4, "vertices": 4, "short_length": 10, "long_length": 20},
        ]

        for shape in shape_data:
            rectangle = deserialize.deserialize(Rectangle, shape)
            self.assertEqual(rectangle.edges, shape["edges"])
            self.assertEqual(rectangle.vertices, shape["vertices"])
            self.assertEqual(rectangle.short_length, shape["short_length"])
            self.assertEqual(rectangle.long_length, shape["long_length"])

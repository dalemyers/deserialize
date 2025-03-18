"""Test deserializing."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize

# pylint: enable=wrong-import-position


class Shape:
    """Represents a shape."""

    edges: int
    vertices: int


class Rectangle(Shape):
    """Represents a rectangle."""

    short_length: int
    long_length: int


def test_rectangle() -> None:
    """Test that rectange deserialization works correctly"""

    shape_data = [
        {"edges": 4, "vertices": 4, "short_length": 4, "long_length": 6},
        {"edges": 4, "vertices": 4, "short_length": 10, "long_length": 20},
    ]

    for shape in shape_data:
        rectangle = deserialize(Rectangle, shape)
        assert rectangle.edges == shape["edges"]
        assert rectangle.vertices == shape["vertices"]
        assert rectangle.short_length == shape["short_length"]
        assert rectangle.long_length == shape["long_length"]

"""Test the constructed decorator."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


@deserialize.constructed(lambda x: setattr(x, "constructed", True))
class Basic:
    """Represents a basic class."""

    one: int


class BasicUnconstructed:
    """Represents a basic class."""

    one: int


def convert_to_radians(instance):
    instance.angle = instance.angle * math.pi / 180


@deserialize.constructed(convert_to_radians)
class PolarCoordinate:
    angle: float
    magnitude: float


class ConstructedTestSuite(unittest.TestCase):
    """Deserialization unhandled test cases."""

    def test_constructed(self):
        """Test that the constructed decoratorworks correctly"""

        data = [{"one": 1}]

        for item in data:
            instance = deserialize.deserialize(Basic, item)
            self.assertTrue(getattr(instance, "constructed"))
            instance = deserialize.deserialize(BasicUnconstructed, item)
            with self.assertRaises(AttributeError):
                getattr(instance, "constructed")

    def test_polar(self):
        """Test that the polar coordinates example from the README works."""

        data = {"angle": 180.0, "magnitude": 42.0}

        instance = deserialize.deserialize(PolarCoordinate, data)

        self.assertTrue(-0.0001 < instance.angle - math.pi < 0.0001)
        self.assertEqual(instance.magnitude, data["magnitude"])

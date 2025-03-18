"""Test the constructed decorator."""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, constructed

# pylint: enable=wrong-import-position


@constructed(lambda x: setattr(x, "constructed", True))
class Basic:
    """Represents a basic class."""

    one: int


class BasicUnconstructed:
    """Represents a basic class."""

    one: int


def convert_to_radians(instance: "PolarCoordinate") -> None:
    """Convert the angle on a PolarCoordinate from degrees to radians."""
    instance.angle = instance.angle * math.pi / 180


@constructed(convert_to_radians)
class PolarCoordinate:
    """Represents a polar coordinate."""

    angle: float
    magnitude: float


def test_constructed() -> None:
    """Test that the constructed decoratorworks correctly"""

    data = [{"one": 1}]

    for item in data:
        instance = deserialize(Basic, item)
        assert getattr(instance, "constructed")
        instance = deserialize(BasicUnconstructed, item)
        with pytest.raises(AttributeError):
            getattr(instance, "constructed")


def test_polar() -> None:
    """Test that the polar coordinates example from the README works."""

    data = {"angle": 180.0, "magnitude": 42.0}

    instance = deserialize(PolarCoordinate, data)

    assert -0.0001 < instance.angle - math.pi < 0.0001
    assert instance.magnitude == data["magnitude"]

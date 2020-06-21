"""Test deserializing."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


@deserialize.ignore("field_2")
class SampleItem:
    """Sample item for use in tests."""

    field_1: int
    field_2: int


def test_keys():
    """Test that root lists deserialize correctly."""

    data = {
        "field_1": 1,
    }

    instance = deserialize.deserialize(SampleItem, data)
    assert data["field_1"] == instance.field_1

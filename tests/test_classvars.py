"""Test deserializing with class vars."""

import os
import sys
from typing import ClassVar

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class BasicType:
    """Basic example."""

    class_var: ClassVar[int] = 1
    member_var: int


def test_basic_classvar():
    """Test that items with a constructor can be deserialized."""
    test_cases = [
        {"member_var": 1},
    ]

    for test_case in test_cases:
        instance = deserialize.deserialize(BasicType, test_case)
        assert test_case["member_var"] == instance.member_var
        assert BasicType.class_var == 1

    test_cases = [
        {"member_var": 1, "class_var": 1},
        {"member_var": 1, "class_var": 2},
        {"class_var": 1},
        {"class_var": 2},
    ]

    for test_case in test_cases:
        with pytest.raises(deserialize.DeserializeException):
            _ = deserialize.deserialize(BasicType, test_case)

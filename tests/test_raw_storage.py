"""Test deserializing with raw storage."""

import os
import sys
from typing import Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, RawStorageMode

# pylint: enable=wrong-import-position


class SimpleStorageClass:
    """Basic storage example."""

    one: int


class BiggerStorageClass:
    """A more complex storage example."""

    one: int
    two: SimpleStorageClass
    three: List[str]


def test_root_simple() -> None:
    """Test that root only storage works."""
    valid_test_cases = [
        {"one": 1},
        {"one": 3},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(
            SimpleStorageClass,
            test_case,
            raw_storage_mode=RawStorageMode.ROOT,
        )
        assert test_case["one"] == instance.one
        assert test_case == instance.__deserialize_raw__


def test_root_bigger() -> None:
    """Test that root only storage works on more complex examples."""
    valid_test_cases: list[dict[str, Any]] = [
        {"one": 1, "two": {"one": 1}, "three": ["one", "two", "three"]},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(
            BiggerStorageClass,
            test_case,
            raw_storage_mode=RawStorageMode.ROOT,
        )
        assert test_case["one"] == instance.one
        assert test_case["two"]["one"] == instance.two.one
        assert test_case["three"] == instance.three
        assert test_case == instance.__deserialize_raw__
        assert not hasattr(instance.two, "__deserialize_raw__")


def test_all_simple() -> None:
    """Test that all property storage works."""
    valid_test_cases = [
        {"one": 1},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(
            SimpleStorageClass,
            test_case,
            raw_storage_mode=RawStorageMode.ALL,
        )
        assert test_case["one"] == instance.one
        assert test_case == instance.__deserialize_raw__


def test_all_bigger() -> None:
    """Test that root only storage works on more complex examples."""
    valid_test_cases: list[dict[str, Any]] = [
        {"one": 1, "two": {"one": 1}, "three": ["one", "two", "three"]},
    ]

    for test_case in valid_test_cases:
        instance = deserialize(
            BiggerStorageClass,
            test_case,
            raw_storage_mode=RawStorageMode.ALL,
        )
        assert test_case["one"] == instance.one
        assert test_case["two"]["one"] == instance.two.one
        assert test_case["three"] == instance.three
        assert test_case == instance.__deserialize_raw__
        assert test_case["two"] == instance.two.__deserialize_raw__

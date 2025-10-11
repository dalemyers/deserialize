"""Test advanced raw storage scenarios."""

import os
import sys
from typing import Dict, List, Union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, RawStorageMode

# pylint: enable=wrong-import-position


def test_raw_storage_mode_child_mode_transitions() -> None:
    """Test RawStorageMode.child_mode() transitions correctly."""

    # NONE -> NONE
    assert RawStorageMode.NONE.child_mode() == RawStorageMode.NONE

    # ROOT -> NONE (children of root don't get raw data)
    assert RawStorageMode.ROOT.child_mode() == RawStorageMode.NONE

    # ALL -> ALL (all levels get raw data)
    assert RawStorageMode.ALL.child_mode() == RawStorageMode.ALL


def test_raw_storage_with_primitives() -> None:
    """Test that raw storage doesn't fail on primitive types."""

    class WithPrimitive:
        """Class with primitive field."""

        value: int

    data = {"value": 42}

    # Primitives can't have __deserialize_raw__ set, but shouldn't error
    instance = deserialize(WithPrimitive, data, raw_storage_mode=RawStorageMode.ALL)
    assert instance.value == 42
    # The instance itself should have raw data
    assert hasattr(instance, "__deserialize_raw__")
    assert instance.__deserialize_raw__ == data


def test_raw_storage_nested_root_mode() -> None:
    """Test that ROOT mode only stores on root, not nested objects."""

    class Inner:
        """Inner class."""

        inner_value: int

    class Outer:
        """Outer class."""

        outer_value: int
        inner: Inner

    data = {"outer_value": 1, "inner": {"inner_value": 2}}

    instance = deserialize(Outer, data, raw_storage_mode=RawStorageMode.ROOT)

    # Root should have raw data
    assert hasattr(instance, "__deserialize_raw__")
    assert instance.__deserialize_raw__ == data

    # Nested object should NOT have raw data
    assert not hasattr(instance.inner, "__deserialize_raw__")


def test_raw_storage_nested_all_mode() -> None:
    """Test that ALL mode stores on all levels."""

    class Inner:
        """Inner class."""

        inner_value: int

    class Outer:
        """Outer class."""

        outer_value: int
        inner: Inner

    data = {"outer_value": 1, "inner": {"inner_value": 2}}

    instance = deserialize(Outer, data, raw_storage_mode=RawStorageMode.ALL)

    # Root should have raw data
    assert hasattr(instance, "__deserialize_raw__")
    assert instance.__deserialize_raw__ == data

    # Nested object SHOULD have raw data
    assert hasattr(instance.inner, "__deserialize_raw__")
    assert instance.inner.__deserialize_raw__ == {"inner_value": 2}


def test_raw_storage_with_lists() -> None:
    """Test raw storage with lists of objects."""

    class Item:
        """Item class."""

        value: int

    class Container:
        """Container with list."""

        items: List[Item]

    data = {"items": [{"value": 1}, {"value": 2}, {"value": 3}]}

    # ALL mode - each item should have raw data
    instance_all = deserialize(Container, data, raw_storage_mode=RawStorageMode.ALL)

    assert hasattr(instance_all, "__deserialize_raw__")
    for i, item in enumerate(instance_all.items):
        assert hasattr(item, "__deserialize_raw__")
        assert item.__deserialize_raw__ == {"value": i + 1}

    # ROOT mode - only container has raw data
    instance_root = deserialize(Container, data, raw_storage_mode=RawStorageMode.ROOT)

    assert hasattr(instance_root, "__deserialize_raw__")
    for item in instance_root.items:
        assert not hasattr(item, "__deserialize_raw__")


def test_raw_storage_deeply_nested() -> None:
    """Test raw storage with deeply nested structures."""

    class Level3:
        """Level 3 class."""

        value: int

    class Level2:
        """Level 2 class."""

        level3: Level3

    class Level1:
        """Level 1 class."""

        level2: Level2

    data = {"level2": {"level3": {"value": 42}}}

    instance = deserialize(Level1, data, raw_storage_mode=RawStorageMode.ALL)

    # Check all levels have raw data
    assert hasattr(instance, "__deserialize_raw__")
    assert instance.__deserialize_raw__ == data

    assert hasattr(instance.level2, "__deserialize_raw__")
    assert instance.level2.__deserialize_raw__ == {"level3": {"value": 42}}

    assert hasattr(instance.level2.level3, "__deserialize_raw__")
    assert instance.level2.level3.__deserialize_raw__ == {"value": 42}


def test_raw_storage_with_union() -> None:
    """Test raw storage with union types."""

    class TypeA:
        """Type A."""

        a_value: int

    class TypeB:
        """Type B."""

        b_value: str

    class WithUnion:
        """Class with union field."""

        either: Union[TypeA, TypeB]

    data_a = {"either": {"a_value": 42}}
    instance_a = deserialize(WithUnion, data_a, raw_storage_mode=RawStorageMode.ALL)

    assert hasattr(instance_a, "__deserialize_raw__")
    assert hasattr(instance_a.either, "__deserialize_raw__")
    assert instance_a.either.__deserialize_raw__ == {"a_value": 42}


def test_raw_storage_with_dict_values() -> None:
    """Test raw storage with dictionary values that are objects."""

    class Value:
        """Value class."""

        data: int

    class WithDict:
        """Class with dict of objects."""

        mapping: Dict[str, Value]

    data = {"mapping": {"key1": {"data": 1}, "key2": {"data": 2}}}

    instance = deserialize(WithDict, data, raw_storage_mode=RawStorageMode.ALL)

    assert hasattr(instance, "__deserialize_raw__")
    assert hasattr(instance.mapping["key1"], "__deserialize_raw__")
    assert instance.mapping["key1"].__deserialize_raw__ == {"data": 1}
    assert hasattr(instance.mapping["key2"], "__deserialize_raw__")
    assert instance.mapping["key2"].__deserialize_raw__ == {"data": 2}


def test_raw_storage_none_mode() -> None:
    """Test that NONE mode doesn't store any raw data."""

    class Inner:
        """Inner class."""

        value: int

    class Outer:
        """Outer class."""

        inner: Inner

    data = {"inner": {"value": 42}}

    instance = deserialize(Outer, data, raw_storage_mode=RawStorageMode.NONE)

    # Nothing should have raw data
    assert not hasattr(instance, "__deserialize_raw__")
    assert not hasattr(instance.inner, "__deserialize_raw__")

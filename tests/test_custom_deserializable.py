"""Test deserializing with specified constructors."""

import os
import sys
from typing import Any, cast

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class Custom(deserialize.CustomDeserializable):
    """Basic constructor example."""

    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def deserialize(cls, value: Any) -> "Custom":
        """Custom deserialization logic."""
        assert isinstance(value, list)
        value = cast(list[Any], value)  # pyright: ignore[reportUnnecessaryCast]
        assert len(value) == 2

        return cls(value[0], value[1])


class CustomContainer:
    """Container for the custom class."""

    identifier: str
    custom: Custom


def test_custom_deserializer() -> None:
    """Test that items with a constructor can be deserialized."""
    custom_instance = deserialize.deserialize(Custom, ["foo", 2])
    assert "foo" == custom_instance.name
    assert 2 == custom_instance.age

    custom_container_instance = deserialize.deserialize(
        CustomContainer, {"identifier": "some id", "custom": ["foo", 2]}
    )
    assert "some id" == custom_container_instance.identifier
    assert "foo" == custom_container_instance.custom.name
    assert 2 == custom_container_instance.custom.age

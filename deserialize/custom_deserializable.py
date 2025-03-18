"""Handlers for case conversions for strings."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CustomDeserializable(Protocol):
    @classmethod
    def deserialize(cls, value: Any) -> "CustomDeserializable":
        """Override this method to implement custom deserialization logic."""
        ...

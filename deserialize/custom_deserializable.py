"""Protocol for custom deserialization."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CustomDeserializable(Protocol):
    """Protocol for classes that implement custom deserialization logic."""

    @classmethod
    def deserialize(cls, value: Any) -> "CustomDeserializable":
        """Override this method to implement custom deserialization logic."""
        raise NotImplementedError()

"""Decorators used for adding functionality to the library."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def allow_unhandled(key_name: str) -> Callable[[type[T]], type[T]]:
    """A decorator function for marking keys as allowed to be unhandled."""

    def store_allow_unhandled_map(class_reference: type[T]) -> type[T]:
        """Store the key map."""
        if not hasattr(class_reference, "__deserialize_allow_unhandled_map__"):
            setattr(class_reference, "__deserialize_allow_unhandled_map__", {})

        class_reference.__deserialize_allow_unhandled_map__[key_name] = True  # type: ignore[attr-defined]

        return class_reference

    return store_allow_unhandled_map


def _should_allow_unhandled(class_reference: type[Any], key_name: str) -> bool:
    """Check if a property is allowed to be unhandled."""

    if not hasattr(class_reference, "__deserialize_allow_unhandled_map__"):
        return False

    return class_reference.__deserialize_allow_unhandled_map__.get(key_name, False)

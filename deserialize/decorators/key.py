"""Decorators used for adding functionality to the library."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def key(property_name: str, key_name: str) -> Callable[[type[T]], type[T]]:
    """A decorator function for mapping key names to properties."""

    def store_key_map(class_reference: type[T]) -> type[T]:
        """Store the key map."""
        if not hasattr(class_reference, "__deserialize_key_map__"):
            setattr(class_reference, "__deserialize_key_map__", {})

        class_reference.__deserialize_key_map__[property_name] = key_name  # type: ignore[attr-defined]

        return class_reference

    return store_key_map


def _get_key(class_reference: type[Any], property_name: str) -> str:
    """Get the key for the given class and property name."""

    if not hasattr(class_reference, "__deserialize_key_map__"):
        return property_name

    return class_reference.__deserialize_key_map__.get(property_name, property_name)

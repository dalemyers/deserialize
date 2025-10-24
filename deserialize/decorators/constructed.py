"""Decorators used for adding functionality to the library."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def constructed(function: Callable[[Any], None]) -> Callable[[type[T]], type[T]]:
    """A decorator function for calling when a class is constructed."""

    def store_constructed(class_reference: type[T]) -> type[T]:
        """Store the key map."""
        setattr(class_reference, "__deserialize_constructed__", function)
        return class_reference

    return store_constructed


def _call_constructed(  # pyright: ignore[reportUnusedFunction] # It is used
    class_reference: type[Any], instance: Any
) -> None:
    """Check if a property is allowed to be unhandled."""

    if not hasattr(class_reference, "__deserialize_constructed__"):
        return

    class_reference.__deserialize_constructed__(instance)

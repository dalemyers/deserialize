"""Decorators used for adding functionality to the library."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def parser(key_name: str, parser_function: Callable[[Any], Any]) -> Callable[[type[T]], type[T]]:
    """A decorator function for mapping parsers to key names."""

    def store_parser_map(class_reference: type[T]) -> type[T]:
        """Store the parser map."""

        if not hasattr(class_reference, "__deserialize_parser_map__"):
            setattr(class_reference, "__deserialize_parser_map__", {})

        class_reference.__deserialize_parser_map__[key_name] = parser_function  # type: ignore[attr-defined]

        return class_reference

    return store_parser_map


def _get_parser(class_reference: type[Any], key_name: str) -> Callable[[Any], Any]:
    """Get the parser for the given class and key name."""

    def identity_parser(value: Any) -> Any:
        """This parser does nothing. It's simply used as the default."""
        return value

    if not hasattr(class_reference, "__deserialize_parser_map__"):
        return identity_parser

    return class_reference.__deserialize_parser_map__.get(key_name, identity_parser)

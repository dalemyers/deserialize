"""Convenience checks for typing."""

import typing
import types
from typing import Any

import deserialize.exceptions

# pylint: disable=protected-access


def is_typing_type(class_reference: Any) -> bool:
    """Check if the supplied type is one defined by the `typing` module."""

    return typing.get_origin(class_reference) is not None


def is_union(type_value: Any) -> bool:
    """Check if a type is an optional type."""

    if not is_typing_type(type_value):
        return False

    return typing.get_origin(type_value) in [typing.Union, types.UnionType]


def union_types(type_value: Any, debug_name: str) -> set[Any]:
    """Return the list of types in a Union."""
    if not is_union(type_value):
        raise deserialize.exceptions.DeserializeException(
            f"Cannot extract union types from non-union type: {type_value} for {debug_name}"
        )

    return set(typing.get_args(type_value))


def is_classvar(type_value: Any) -> bool:
    """Check if a type is a ClassVar type."""

    if not is_typing_type(type_value):
        return False

    return typing.get_origin(type_value) == typing.ClassVar


def is_list(type_value: Any) -> bool:
    """Check if a type is a list type."""

    if type_value is list:
        return True

    if not is_typing_type(type_value):
        return False

    if not hasattr(type_value, "__origin__"):
        return False

    return typing.get_origin(type_value) == list


def list_content_type(type_value: Any, debug_name: str) -> Any:
    """Strip the list wrapper from a type.

    e.g. list[int] -> int
    """

    if not is_list(type_value):
        raise TypeError(f"{type_value} is not a list type for {debug_name}")

    args = typing.get_args(type_value)

    if len(args) == 0:
        return typing.Any

    if len(args) == 1:
        return args[0]

    raise TypeError(f"{type_value} should only have a single type for {debug_name}")


def is_dict(type_value: Any) -> bool:
    """Check if a type is a dict type."""

    if type_value is dict:
        return True

    if not is_typing_type(type_value):
        return False

    if not hasattr(type_value, "__origin__"):
        return False

    return typing.get_origin(type_value) == dict


def dict_content_types(type_value: Any, debug_name: str) -> tuple[Any, ...]:
    """Return the content types for a dictionary.

    e.g. dict[str, int] -> (str, int)
    """

    if not is_dict(type_value):
        raise TypeError(f"{type_value} is not a dict type for {debug_name}")

    return typing.get_args(type_value)

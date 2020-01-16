"""Convenience checks for typing."""

import sys
import typing

import deserialize.exceptions

# pylint: disable=protected-access


def is_typing_type(class_reference):
    """Check if the supplied type is one defined by the `typing` module.

    This behaves differently on 3.6 and 3.7+
    """

    if sys.version_info < (3, 7):
        # Union/Optional is a special case since it doesn't inherit.

        # Not everything has the __origin__ member
        if hasattr(class_reference, "__origin__"):
            if class_reference.__origin__ == typing.Union:
                return True

        # pylint: disable=no-member
        if isinstance(class_reference, typing._TypeAlias):
            return True

        if isinstance(class_reference, typing.GenericMeta):
            return True

        return class_reference.__module__ == "typing"
        # pylint: enable=no-member

    return isinstance(class_reference, typing._GenericAlias)


def is_union(type_value):
    """Check if a type is an optional type."""

    if not is_typing_type(type_value):
        return False

    return type_value.__origin__ == typing.Union


def union_types(type_value, debug_name):
    """Return the list of types in a Union."""
    if not is_union(type_value):
        raise deserialize.exceptions.DeserializeException(
            f"Cannot extract union types from non-union type: {type_value} for {debug_name}"
        )

    return set(type_value.__args__)


def is_classvar(type_value):
    """Check if a type is a ClassVar type."""

    if not is_typing_type(type_value):
        return False

    if sys.version_info < (3, 7):
        # pylint: disable=unidiomatic-typecheck
        return type(type_value) == type(typing.ClassVar)
        # pylint: enable=unidiomatic-typecheck

    return type_value.__origin__ == typing.ClassVar


def is_list(type_value):
    """Check if a type is a list type."""

    if not is_typing_type(type_value):
        return False

    if not hasattr(type_value, "__origin__"):
        return False

    if sys.version_info < (3, 7):
        return type_value.__origin__ == typing.List

    return type_value.__origin__ == list


def list_content_type(type_value, debug_name):
    """Strip the List wrapper from a type.

    e.g. List[int] -> int
    """

    if not is_list(type_value):
        raise TypeError(f"{type_value} is not a List type for {debug_name}")

    return type_value.__args__[0]


def is_dict(type_value):
    """Check if a type is a dict type."""

    if type_value is dict:
        return True

    if not is_typing_type(type_value):
        return False

    if not hasattr(type_value, "__origin__"):
        return False

    if sys.version_info < (3, 7):
        return type_value.__origin__ == typing.Dict

    return type_value.__origin__ == dict


def dict_content_types(type_value, debug_name):
    """Return the content types for a dictionay.

    e.g. Dict[str, int] -> (str, int)
    """

    if not is_dict(type_value):
        raise TypeError(f"{type_value} is not a Dict type for {debug_name}")

    return type_value.__args__[0], type_value.__args__[1]

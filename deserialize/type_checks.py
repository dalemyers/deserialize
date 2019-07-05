"""Convenience checks for typing."""

import sys
import typing

import deserialize.exceptions

#pylint: disable=protected-access

def is_typing_type(class_reference):
    """Check if the supplied type is one defined by the `typing` module.

    This behaves differently on 3.6 and 3.7+
    """

    if sys.version_info < (3, 7):
        # Union/Optional is a special case since it doesn't inherit.
        try:
            if class_reference.__origin__ == typing.Union:
                return True
        except:
            # Not everything has the __origin__ member
            pass

        if isinstance(class_reference, typing._TypeAlias):
            return True

        return isinstance(class_reference, typing.GenericMeta)

    return isinstance(class_reference, typing._GenericAlias)


def is_union(type_value):
    """Check if a type is an optional type."""

    if not is_typing_type(type_value):
        return False

    return type_value.__origin__ == typing.Union


def union_types(type_value):
    """Return the list of types in a Union."""
    if not is_union(type_value):
        raise deserialize.exceptions.DeserializeException(f"Cannot extract union types from non-union type: {type_value}")

    return list(type_value.__args__)


def is_list(type_value):
    """Check if a type is a list type."""

    if not is_typing_type(type_value):
        return False

    try:
        if sys.version_info < (3, 7):
            return type_value.__origin__ == typing.List
        return type_value.__origin__ == list
    except AttributeError:
        return False


def list_content_type(type_value):
    """Strip the List wrapper from a type.

    e.g. List[int] -> int
    """

    if not is_list(type_value):
        raise TypeError(f"{type_value} is not a List type")

    return type_value.__args__[0]


def is_dict(type_value):
    """Check if a type is a dict type."""

    if not is_typing_type(type_value):
        return False

    try:
        if sys.version_info < (3, 7):
            return type_value.__origin__ == typing.Dict
        return type_value.__origin__ == dict
    except AttributeError:
        return False


def dict_content_types(type_value):
    """Return the content types for a dictionay.

    e.g. Dict[str, int] -> (str, int)
    """

    if not is_dict(type_value):
        raise TypeError(f"{type_value} is not a Dict type")

    return type_value.__args__[0], type_value.__args__[1]

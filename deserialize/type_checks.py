"""Convenience checks for typing."""

import typing

#pylint: disable=protected-access


def is_base_type(type_value):
    """Check if a type is a base type or not."""
    if isinstance(type_value, typing._GenericAlias):
        return False

    return attribute_type_name(type_value) is None



def is_optional(type_value):
    """Check if a type is an optional type."""

    if not isinstance(type_value, typing._GenericAlias):
        return False

    if len(type_value.__args__) != 2:
        return False

    return type_value.__args__[1] == type(None)


def optional_content_type(type_value):
    """Strip the Optional wrapper from a type.

    e.g. Optional[int] -> int
    """

    if not is_optional(type_value):
        raise TypeError(f"{type_value} is not an Optional type")

    return type_value.__args__[0]


def is_list(type_value):
    """Check if a type is a list type."""

    if not isinstance(type_value, typing._GenericAlias):
        return False

    return type_value._name == "List"


def list_content_type(type_value):
    """Strip the List wrapper from a type.

    e.g. List[int] -> int
    """

    if not is_list(type_value):
        raise TypeError(f"{type_value} is not a List type")

    return type_value.__args__[0]


def is_dict(type_value):
    """Check if a type is a dict type."""

    if not isinstance(type_value, typing._GenericAlias):
        return False

    return type_value._name == "Dict"


def dict_content_types(type_value):
    """Return the content types for a dictionay.

    e.g. Dict[str, int] -> (str, int)
    """

    if not is_dict(type_value):
        raise TypeError(f"{type_value} is not a List type")

    return type_value.__args__[0], type_value.__args__[1]


def attribute_type_name(type_value):
    """Return the name of the attribute type (if there is one).

    If this is a non-typing type, None will be returned.
    """

    if not isinstance(type_value, typing._GenericAlias):
        return None

    return type_value._name

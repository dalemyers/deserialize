"""A module for deserializing data to Python objects."""

#pylint: disable=unidiomatic-typecheck
#pylint: disable=protected-access
#pylint: disable=too-many-branches
#pylint: disable=wildcard-import

import enum
import functools
import typing
from typing import Any, Callable, Dict, List, Optional, Union

from deserialize.decorators import ignore, _should_ignore, key, _get_key, parser, _get_parser
from deserialize.exceptions import DeserializeException, InvalidBaseTypeException
from deserialize.type_checks import *


def deserialize(class_reference, data):
    """Deserialize data to a Python object."""

    if not isinstance(data, dict) and not isinstance(data, list):
        raise InvalidBaseTypeException("Only lists and dictionaries are supported as base raw data types")

    try:
        name = class_reference.__name__
    except AttributeError:
        name = str(class_reference)

    return _deserialize(class_reference, data, name)


def _deserialize(class_reference, data, debug_name):
    """Deserialize data to a Python object, but allow base types"""

    if is_union(class_reference):
        valid_types = union_types(class_reference)
        for valid_type in valid_types:
            try:
                return _deserialize(valid_type, data, debug_name)
            except:
                pass

    if isinstance(data, dict):
        return _deserialize_dict(class_reference, data, debug_name)

    if isinstance(data, list):
        return _deserialize_list(class_reference, data, debug_name)

    if not is_typing_type(class_reference) and issubclass(class_reference, enum.Enum):
        try:
            return class_reference(data)
        #pylint:disable=bare-except
        except:
        #pylint:enable=bare-except
            # This will be handled at the end
            pass

    # If we still have a type from the typing module, we don't know how to
    # handle it
    if is_typing_type(class_reference):
        raise DeserializeException(f"Unsupported deserialization type: {class_reference}")

    # Whatever we have left now is either correct, or invalid
    if isinstance(data, class_reference):
        return data

    raise DeserializeException(f"Cannot deserialize '{type(data)}' to '{class_reference}' for '{debug_name}'")



def _deserialize_list(class_reference, list_data, debug_name):

    if not isinstance(list_data, list):
        raise DeserializeException(f"Cannot deserialize '{type(list_data)}' as a list.")

    if not is_list(class_reference):
        raise DeserializeException(f"Cannot deserialize a list to '{class_reference}'")

    list_content_type_value = list_content_type(class_reference)

    output = []

    for index, item in enumerate(list_data):
        deserialized = _deserialize(list_content_type_value, item, f"{debug_name}[{index}]")
        output.append(deserialized)

    return output


def _deserialize_dict(class_reference, data, debug_name):
    """Deserialize a dictionary to a Python object."""

    # Check if we are doing a straightforward dictionary parse first, or if it
    # has to be deserialized
    if is_dict(class_reference):
        key_type, value_type = dict_content_types(class_reference)
        result = {}

        for dict_key, dict_value in data.items():

            if not isinstance(dict_key, key_type):
                raise DeserializeException(f"Could not deserialize key {dict_key} to type {key_type} for {debug_name}")

            result[dict_key] = _deserialize(value_type, dict_value, f"{debug_name}.{dict_key}")

        return result

    # It wasn't a straight forward dictionary, so we are in deserialize mode

    hints = typing.get_type_hints(class_reference)

    if len(hints) == 0:
        raise DeserializeException(f"Could not deserialize {data} into {class_reference} due to lack of type hints")

    class_instance = class_reference()

    for attribute_name, attribute_type in hints.items():
        if _should_ignore(class_reference, attribute_name):
            continue

        property_key = _get_key(class_reference, attribute_name)
        parser_function = _get_parser(class_reference, property_key)
        property_value = parser_function(data.get(property_key))

        deserialized_value = _deserialize(attribute_type, property_value, f"{debug_name}.{attribute_name}")
        setattr(class_instance, attribute_name, deserialized_value)

    return class_instance

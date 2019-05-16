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

    # Shortcut out if we have already got the matching type.
    # We shouldn't need the check to see if this is a generic type instance
    # since the class_reference isinstance check should just return False if it
    # isn't. The problem is that any types which inherit from _GenericAlias have
    # overridden the isinstance check and it throws an exception if you try. To
    # avoid this, we do the explicit check that it isn't a generic instance
    # first, short circuiting the operator if it is.
    if not is_typing_type(class_reference):
        try:
            if isinstance(data, class_reference):
                return data
        # The isinstance check throws an exception on 3.6
        except TypeError:
            pass

    if isinstance(data, dict):
        return _deserialize_dict(class_reference, data, debug_name)

    if isinstance(data, list):
        return _deserialize_list(class_reference, data, debug_name)

    if issubclass(class_reference, enum.Enum):
        try:
            return class_reference(data)
        #pylint:disable=bare-except
        except:
        #pylint:enable=bare-except
            # This will be handled at the end
            pass

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

        # Check for optionals first. We check if it's None, finish if so.
        # Otherwise we can hoist out the type and continue
        if is_optional(attribute_type):
            if property_value is None:
                setattr(class_instance, attribute_name, None)
                continue
            else:
                attribute_type = optional_content_type(attribute_type)

        # If the types match straight up, we can set and continue
        try:
            if isinstance(property_value, attribute_type):
                setattr(class_instance, attribute_name, property_value)
                continue
        except:
            pass

        # Check if we have something we need to parse further or not.
        # If it is a base type (i.e. not a wrapper of some kind), then we can
        # go ahead and parse it directly without needing to iterate in any way.
        if not is_typing_type(attribute_type):
            custom_type_instance = _deserialize(attribute_type, property_value, f"{debug_name}.{attribute_name}")
            setattr(class_instance, attribute_name, custom_type_instance)
            continue

        # Lists and dictionaries remain
        if is_list(attribute_type):
            setattr(class_instance, attribute_name, _deserialize_list(attribute_type, property_value, f"{debug_name}.{attribute_name}"))
            continue

        if is_dict(attribute_type):

            if not isinstance(property_value, dict):
                raise DeserializeException(f"Value '{property_value}' is type '{type(property_value)}' not 'dict'")

            # If there are no values, then the types automatically do match
            if len(property_value) == 0:
                setattr(class_instance, attribute_name, property_value)
                continue

            key_type, value_type = dict_content_types(attribute_type)

            result = {}

            for item_key, item_value in property_value.items():

                if type(item_key) != key_type:
                    raise DeserializeException(f"Key '{item_key}' is type '{type(item_key)}' not '{key_type}'")

                # If the types match, we can just set it and move on
                if type(item_value) == value_type:
                    result[item_key] = item_value
                    continue

                # We have to deserialize (it will throw on failure)
                result[item_key] = _deserialize(value_type, item_value, f"{debug_name}.{item_key}")

            setattr(class_instance, attribute_name, result)
            continue

        raise DeserializeException(f"Unexpected type '{type(property_value)}' for attribute '{attribute_name}' on '{debug_name}'. Expected '{attribute_type}'")

    return class_instance

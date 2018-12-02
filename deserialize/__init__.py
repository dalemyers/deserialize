"""A module for deserializing data to Python objects."""

import functools
import typing
from typing import Any, Callable, Dict, List, Optional, Union

#pylint: disable=unidiomatic-typecheck
#pylint: disable=protected-access
#pylint: disable=too-many-branches

__version__ = "0.3"


_KEY_MAP: Dict[Any, Dict[str, str]] = {}
_PARSER_MAP: Dict[Any, Dict[str, Callable]] = {}


def key(property_name, key_name):
    """A decorator function for mapping key names to properties."""

    def store_key_map(class_reference):
        """Store the key map."""
        if _KEY_MAP.get(class_reference) is None:
            _KEY_MAP[class_reference] = {}
        _KEY_MAP[class_reference][property_name] = key_name
        return class_reference

    return store_key_map


def _get_key(class_reference, property_name):
    """Get the key for the given class and property name."""

    class_map = _KEY_MAP.get(class_reference)

    if class_map is None:
        return property_name

    return class_map.get(property_name, property_name)


def parser(key_name, parser_function):
    """A decorator function for mapping parsers to key names."""

    def store_parser_map(class_reference):
        """Store the parser map."""
        if _PARSER_MAP.get(class_reference) is None:
            _PARSER_MAP[class_reference] = {}
        _PARSER_MAP[class_reference][key_name] = parser_function
        return class_reference

    return store_parser_map


def _get_parser(class_reference, key_name):
    """Get the parser for the given class and keu name."""

    def identity_parser(value):
        """This parser does nothing. It's simply used as the default."""
        return value

    class_map = _PARSER_MAP.get(class_reference)

    if class_map is None:
        return identity_parser

    return class_map.get(key_name, identity_parser)



class DeserializeException(Exception):
    """Represents an error deserializing a value."""
    pass


def deserialize(class_reference, data):
    """Deserialize data to a Python object."""
    if not isinstance(data, dict):
        raise DeserializeException(f"Data must be a dictionary")

    return _deserialize_dict(class_reference, data)


def _deserialize_dict(class_reference, data):
    """Deserialize a dictionary to a Python object."""

    hints = typing.get_type_hints(class_reference)

    if len(hints) == 0:
        raise DeserializeException(f"Could not deserialize {data} into {class_reference}")

    class_instance = class_reference()

    for attribute_name, attribute_type in hints.items():
        property_key = _get_key(class_reference, attribute_name)
        property_value_unparsed = data.get(property_key)
        parser_function = _get_parser(class_reference, property_key)
        property_value = parser_function(property_value_unparsed)
        property_type = type(property_value)

        try:
            attribute_type_name = attribute_type._name
        except AttributeError:
            attribute_type_name = None

        # Check for optionals first. We check if it's None, finish if so.
        # Otherwise we can hoist out the type and continue
        try:
            if len(attribute_type.__args__) == 2 and attribute_type.__args__[1] == type(None):
                if property_value is None:
                    setattr(class_instance, attribute_name, None)
                    continue
                else:
                    attribute_type = attribute_type.__args__[0]
        except AttributeError:
            # A base type will not have the __args__ attribute
            pass

        # If the types match straight up, we can set and continue
        if property_type == attribute_type:
            setattr(class_instance, attribute_name, property_value)
            continue

        # If we don't have an attribute type name, we have a custom type, so
        # handle it
        if attribute_type_name is None:
            custom_type_instance = deserialize(attribute_type, property_value)
            setattr(class_instance, attribute_name, custom_type_instance)
            continue

        # Lists and dictionaries remain
        if attribute_type_name == "List":
            # If there are no values, then the types automatically do match

            if not isinstance(property_value, list):
                raise DeserializeException(f"Unexpected type '{type(property_value)}'. Expected '{type(list)}'")

            if len(property_value) == 0:
                setattr(class_instance, attribute_name, property_value)
                continue

            list_content_type = attribute_type.__args__[0]

            result = []

            for item in property_value:
                if type(item) == list_content_type:
                    result.append(item)
                else:
                    attempted_instance = deserialize(list_content_type, item)
                    result.append(attempted_instance)

            setattr(class_instance, attribute_name, result)
            continue

        if attribute_type_name == "Dict":
            # If there are no values, then the types automatically do match
            if len(property_value) == 0:
                setattr(class_instance, attribute_name, property_value)
                continue

            key_type = attribute_type.__args__[0]
            value_type = attribute_type.__args__[1]

            result = {}

            for item_key, item_value in property_value.items():

                if type(item_key) != key_type:
                    raise DeserializeException(f"Key '{item_key}' is type '{type(item_key)}' not '{key_type}'")

                # If the types match, we can just set it and move on
                if type(item_value) == value_type:
                    result[item_key] = item_value
                    continue

                # We have to deserialize
                item_deserialized = deserialize(value_type, item_value)
                result[item_key] = item_deserialized

            setattr(class_instance, attribute_name, result)
            continue

        raise DeserializeException(f"Unexpected type '{property_type}' for attribute '{attribute_name}'. Expected '{attribute_type}'")

    return class_instance

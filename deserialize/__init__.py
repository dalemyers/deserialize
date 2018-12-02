"""A module for deserializing data to Python objects."""

import typing
from typing import Dict, List, Optional, Union

#pylint: disable=unidiomatic-typecheck
#pylint: disable=protected-access
#pylint: disable=too-many-branches

__version__ = "0.2"

class DeserializeException(Exception):
    """Represents an error deserializing a value."""
    pass


def deserialize(class_reference, data):
    """Deserialize data to a Python object."""

    def _is_base_type(value):
        """Check if this is a base type that we don't have to do anything with."""
        return type(value) in [int, float, str, bool]

    hints = typing.get_type_hints(class_reference)

    if len(hints) == 0:
        raise DeserializeException(f"Could not deserialize {data} into {class_reference}")

    class_instance = class_reference()

    for attribute_name, attribute_type in hints.items():
        property_value = data.get(attribute_name)
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
                if _is_base_type(item):
                    if type(item) != list_content_type:
                        raise DeserializeException(f"Unexpected type '{type(item)}' for list item '{item}'. Expected '{list_content_type}'")
                    else:
                        result.append(item)
                else:
                    result.append(deserialize(list_content_type, item))

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

            for key, value in property_value.items():

                if type(key) != key_type:
                    raise DeserializeException(f"Key '{key}' is type '{type(key)}' not '{key_type}'")

                # If the types match, we can just set it and move on
                if type(value) == value_type:
                    result[key] = value
                    continue

                # We have to deserialize
                item_deserialized = deserialize(value_type, value)
                result[key] = item_deserialized

            setattr(class_instance, attribute_name, result)
            continue

        raise DeserializeException(f"Unexpected type '{property_type}' for attribute '{attribute_name}'. Expected '{attribute_type}'")

    return class_instance

"""A module for deserializing data to Python objects."""

# pylint: disable=unidiomatic-typecheck
# pylint: disable=protected-access
# pylint: disable=too-many-branches
# pylint: disable=wildcard-import

import enum
import functools
import typing
from typing import Any, Callable, Dict, List, Optional, Union

from deserialize.conversions import camel_case, pascal_case
from deserialize.decorators import constructed, _call_constructed
from deserialize.decorators import default, _get_default, _has_default
from deserialize.decorators import (
    downcast_field,
    _get_downcast_field,
    downcast_identifier,
    _get_downcast_class,
    allow_downcast_fallback,
    _allows_downcast_fallback,
)
from deserialize.decorators import ignore, _should_ignore
from deserialize.decorators import key, _get_key
from deserialize.decorators import parser, _get_parser
from deserialize.decorators import auto_snake, _uses_auto_snake
from deserialize.decorators import allow_unhandled, _should_allow_unhandled

from deserialize.exceptions import (
    DeserializeException,
    InvalidBaseTypeException,
    NoDefaultSpecifiedException,
    UndefinedDowncastException,
    UnhandledFieldException,
)
from deserialize.type_checks import *


class RawStorageMode(enum.Enum):
    """The storage mode for the raw data on each object.

    If a store mode is set, the data will be stored in the attribute named:
    `__deserialize_raw__`
    """

    # Do not store the raw data at all
    none = "none"

    # Only store the data on the root node
    root = "root"

    # Store on all objects (WARNING: This can use a significant amount of memory)
    all = "all"

    def child_mode(self) -> "RawStorageMode":
        """Determine the mode for child parsing.

        When we move to the next child iteration, we need to change mode
        in some cases. For instance, if we only store the root node, then we
        need to set all the children to not be stored.

        :raises Exception: If we get an unexpected storage mode

        :returns: The child raw storage mode
        """
        if self == RawStorageMode.none:
            return RawStorageMode.none

        if self == RawStorageMode.root:
            return RawStorageMode.none

        if self == RawStorageMode.all:
            return RawStorageMode.all

        raise DeserializeException(f"Unexpected raw storage mode: {self}")


# pylint: disable=function-redefined
def deserialize(class_reference, data, *, throw_on_unhandled: bool = False, raw_storage_mode: RawStorageMode = RawStorageMode.none):  # type: ignore
    """Deserialize data to a Python object."""

    if not isinstance(data, dict) and not isinstance(data, list):
        raise InvalidBaseTypeException(
            "Only lists and dictionaries are supported as base raw data types"
        )

    if hasattr(class_reference, "__name__"):
        name = class_reference.__name__
    else:
        name = str(class_reference)

    return _deserialize(
        class_reference,
        data,
        name,
        throw_on_unhandled=throw_on_unhandled,
        raw_storage_mode=raw_storage_mode,
    )


# pylint: enable=function-redefined

# pylint:disable=too-many-return-statements
def _deserialize(
    class_reference, data, debug_name, *, throw_on_unhandled: bool, raw_storage_mode: RawStorageMode
):
    """Deserialize data to a Python object, but allow base types"""

    # In here we try and use some "heuristics" to deserialize. We have 2 main
    # options to do this. For the first, we can take the expected type and try
    # and deserialize the data to that and show any errors. The other option is
    # to take the data, and try and determine the types and deserialize that
    # way. We do a mix of both.
    #
    # For example, we check if we have an any type or None type first and return
    # early, since we can't deserialize directly to those (since that doesn't
    # make any sense). But then later, we can't go for a list directly to a
    # type, so we have to go through each item in the data, and iterate.
    #
    # This produces quite a complex interweaving of operations. The general
    # approach I've found to work is to try and do specific type checks first,
    # then handle collection data, then any other types afterwards. That's not
    # set in stone though.

    def finalize(value: Optional[Any]) -> Optional[Any]:
        """Run through any finalization steps before returning the value."""

        # Set raw data where applicable
        if raw_storage_mode in [RawStorageMode.root, RawStorageMode.all]:
            # We can't set attributes on primitive types
            if hasattr(value, "__dict__"):
                setattr(value, "__deserialize_raw__", data)

        return value

    if class_reference == Any:
        return finalize(data)

    # Check if it's None (since things like Union[int, Optional[str]] become
    # Union[int, str, None] so we end up iterating against it)
    if class_reference == type(None) and data is None:
        return finalize(None)

    if is_union(class_reference):
        valid_types = union_types(class_reference, debug_name)
        exceptions = []
        for valid_type in valid_types:
            try:
                return finalize(
                    _deserialize(
                        valid_type,
                        data,
                        debug_name,
                        throw_on_unhandled=throw_on_unhandled,
                        raw_storage_mode=raw_storage_mode.child_mode(),
                    )
                )
            except DeserializeException as ex:
                exceptions.append(str(ex))

        exception_message = (
            f"Cannot deserialize '{type(data)}' to '{class_reference}' for '{debug_name}' ->"
        )
        for exception in exceptions:
            exception_lines = exception.split("\n")
            sub_message = f"\n\t* {exception_lines[0]}"
            for line in exception_lines[1:]:
                sub_message += f"\n\t{line}"
            exception_message += sub_message
        raise DeserializeException(exception_message)

    if isinstance(data, dict):
        return finalize(
            _deserialize_dict(
                class_reference,
                data,
                debug_name,
                throw_on_unhandled=throw_on_unhandled,
                raw_storage_mode=raw_storage_mode,
            )
        )

    if isinstance(data, list):
        return finalize(
            _deserialize_list(
                class_reference,
                data,
                debug_name,
                throw_on_unhandled=throw_on_unhandled,
                raw_storage_mode=raw_storage_mode,
            )
        )

    if not is_typing_type(class_reference) and issubclass(class_reference, enum.Enum):
        try:
            return finalize(class_reference(data))
        # pylint:disable=bare-except
        except:
            # pylint:enable=bare-except
            # This will be handled at the end
            pass

    # If we still have a type from the typing module, we don't know how to
    # handle it
    if is_typing_type(class_reference):
        # The data should not be None if we have a type that got here. Optionals
        # are handled by unions above, so if we are here, it's a non-optional
        # type and therefore should not be None.
        if data is None:
            raise DeserializeException(
                f"No value for '{debug_name}'. Expected value of type '{class_reference}'"
            )

        raise DeserializeException(
            f"Unsupported deserialization type: {class_reference} for {debug_name}"
        )

    # Whatever we have left now is either correct, or invalid
    if isinstance(data, class_reference):
        return finalize(data)

    raise DeserializeException(
        f"Cannot deserialize '{type(data)}' to '{class_reference}' for '{debug_name}'"
    )


# pylint:enable=too-many-return-statements


def _deserialize_list(
    class_reference,
    list_data,
    debug_name,
    *,
    throw_on_unhandled: bool,
    raw_storage_mode: RawStorageMode,
):

    if not isinstance(list_data, list):
        raise DeserializeException(
            f"Cannot deserialize '{type(list_data)}' as a list for {debug_name}."
        )

    if not is_list(class_reference):
        raise DeserializeException(
            f"Cannot deserialize a list to '{class_reference}' for {debug_name}"
        )

    list_content_type_value = list_content_type(class_reference, debug_name)

    output = []

    for index, item in enumerate(list_data):
        deserialized = _deserialize(
            list_content_type_value,
            item,
            f"{debug_name}[{index}]",
            throw_on_unhandled=throw_on_unhandled,
            raw_storage_mode=raw_storage_mode.child_mode(),
        )
        output.append(deserialized)

    return output


def _deserialize_dict(
    class_reference, data, debug_name, *, throw_on_unhandled: bool, raw_storage_mode: RawStorageMode
):
    """Deserialize a dictionary to a Python object."""

    # Check if we are doing a straightforward dictionary parse first, or if it
    # has to be deserialized

    remaining_properties = set(data.keys())

    if not isinstance(data, dict):
        raise DeserializeException(
            f"Data was not dict for instance: {class_reference} for {debug_name}"
        )

    if is_dict(class_reference):
        if class_reference is dict:
            # If types of dictionary entries are not defined, do not deserialize
            return data
        key_type, value_type = dict_content_types(class_reference, debug_name)
        result = {}

        for dict_key, dict_value in data.items():

            if key_type != Any and not isinstance(dict_key, key_type):
                raise DeserializeException(
                    f"Could not deserialize key {dict_key} to type {key_type} for {debug_name}"
                )

            result[dict_key] = _deserialize(
                value_type,
                dict_value,
                f"{debug_name}.{dict_key}",
                throw_on_unhandled=throw_on_unhandled,
                raw_storage_mode=raw_storage_mode.child_mode(),
            )

            remaining_properties.remove(dict_key)

        if throw_on_unhandled and len(remaining_properties) > 0:
            raise UnhandledFieldException(
                f"The following field was unhandled: {list(remaining_properties)[0]} for {debug_name}"
            )

        return result

    # It wasn't a straight forward dictionary, so we are in deserialize mode

    class_instance = None

    class_reference_downcast_field = _get_downcast_field(class_reference)
    if class_reference_downcast_field:
        downcast_value = data[class_reference_downcast_field]
        new_reference = _get_downcast_class(class_reference, downcast_value)
        if new_reference is None:
            if _allows_downcast_fallback(class_reference):
                return _deserialize(
                    Dict[Any, Any],
                    data,
                    debug_name,
                    throw_on_unhandled=throw_on_unhandled,
                    raw_storage_mode=raw_storage_mode.child_mode(),
                )
            raise UndefinedDowncastException(
                f"Could not find subclass of {class_reference} with downcast identifier '{downcast_value}' for {debug_name}"
            )
        class_reference = new_reference

    class_instance = class_reference.__new__(class_reference)

    handled_fields = set()

    hints = typing.get_type_hints(class_reference)

    if len(hints) == 0:
        raise DeserializeException(
            f"Could not deserialize {data} into {class_reference} due to lack of type hints ({debug_name})"
        )

    for attribute_name, attribute_type in hints.items():
        if _should_ignore(class_reference, attribute_name):
            continue

        property_key = _get_key(class_reference, attribute_name)
        parser_function = _get_parser(class_reference, property_key)

        if is_classvar(attribute_type):
            if property_key in data:
                raise DeserializeException(
                    f"ClassVars cannot be set: {debug_name}.{attribute_name}"
                )
            continue

        if _uses_auto_snake(class_reference) and attribute_name.lower() != attribute_name:
            raise DeserializeException(
                f"When using auto_snake, all properties must be snake cased. Error on: {debug_name}.{attribute_name}"
            )

        using_default = False

        if property_key in data:
            value = data[property_key]
            handled_fields.add(property_key)
            property_value = parser_function(value)
        elif _uses_auto_snake(class_reference) and camel_case(property_key) in data:
            value = data[camel_case(property_key)]
            handled_fields.add(camel_case(property_key))
            property_value = parser_function(value)
        elif _uses_auto_snake(class_reference) and pascal_case(property_key) in data:
            value = data[pascal_case(property_key)]
            handled_fields.add(pascal_case(property_key))
            property_value = parser_function(value)
        else:
            if _has_default(class_reference, attribute_name):
                deserialized_value = _get_default(class_reference, attribute_name)
                using_default = True
            else:
                if not is_union(attribute_type) or type(None) not in union_types(
                    attribute_type, debug_name
                ):
                    raise DeserializeException(
                        f"Unexpected missing value for: {debug_name}.{attribute_name}"
                    )
                property_value = parser_function(None)

        if not using_default:
            deserialized_value = _deserialize(
                attribute_type,
                property_value,
                f"{debug_name}.{attribute_name}",
                throw_on_unhandled=throw_on_unhandled,
                raw_storage_mode=raw_storage_mode.child_mode(),
            )

        setattr(class_instance, attribute_name, deserialized_value)

    unhandled = set(data.keys()) - handled_fields

    if throw_on_unhandled and len(unhandled) > 0:
        filtered_unhandled = [
            key for key in unhandled if not _should_allow_unhandled(class_reference, key)
        ]
        if len(filtered_unhandled) > 0:
            raise UnhandledFieldException(
                f"Unhandled field: {list(filtered_unhandled)[0]} for {debug_name}"
            )

    _call_constructed(class_reference, class_instance)

    return class_instance

"""A module for deserializing data to Python objects."""

# pylint: disable=protected-access
# pylint: disable=too-many-branches

import enum
import inspect
from typing import Any, Annotated, TypeVar, cast, overload

from deserialize.conversions import camel_case, pascal_case
from deserialize.custom_deserializable import CustomDeserializable
from deserialize.decorators import (
    constructed,
    _call_constructed,
)
from deserialize.decorators import default
from deserialize.decorators import (
    downcast_field,
    downcast_identifier,
    _get_downcast_class,
    allow_downcast_fallback,
)
from deserialize.decorators import ignore
from deserialize.decorators import key
from deserialize.decorators import parser
from deserialize.decorators import auto_snake
from deserialize.decorators import (
    allow_unhandled,
    _should_allow_unhandled,
)

from deserialize.exceptions import (
    DeserializeException,
    InvalidBaseTypeException,
    UndefinedDowncastException,
    UnhandledFieldException,
)
from deserialize.raw_storage_mode import RawStorageMode
from deserialize.type_checks import (
    is_classvar,
    is_union,
    union_types,
    is_typing_type,
    is_list,
    is_dict,
    list_content_type,
    dict_content_types,
)
from deserialize.metadata_cache import get_class_metadata
from deserialize.field import Field

# Type variable for deserialization
T = TypeVar("T")


# Public API - explicitly declare re-exports for type checkers
__all__ = [
    # Main function
    "deserialize",
    # Decorators
    "constructed",
    "default",
    "downcast_field",
    "downcast_identifier",
    "allow_downcast_fallback",
    "ignore",
    "key",
    "parser",
    "auto_snake",
    "allow_unhandled",
    # Exceptions
    "DeserializeException",
    "InvalidBaseTypeException",
    "UndefinedDowncastException",
    "UnhandledFieldException",
    # Enums
    "RawStorageMode",
    # Type checks
    "is_classvar",
    "is_union",
    "union_types",
    "is_typing_type",
    "is_list",
    "is_dict",
    "list_content_type",
    "dict_content_types",
    # Field annotation support
    "Field",
    "Annotated",
    # Custom deserialization protocol
    "CustomDeserializable",
    # Utilities
    "camel_case",
    "pascal_case",
    "get_class_metadata",
]


@overload
def deserialize(
    class_reference: type[T],
    data: Any,
    *,
    throw_on_unhandled: bool = False,
    raw_storage_mode: RawStorageMode = RawStorageMode.NONE,
) -> T: ...


@overload
def deserialize(
    class_reference: Any,
    data: Any,
    *,
    throw_on_unhandled: bool = False,
    raw_storage_mode: RawStorageMode = RawStorageMode.NONE,
) -> Any: ...


# pylint: disable=function-redefined
def deserialize(  # type: ignore
    class_reference: type[T],
    data: dict[Any, Any] | list[Any],
    *,
    throw_on_unhandled: bool = False,
    raw_storage_mode: RawStorageMode = RawStorageMode.NONE,
) -> T:
    """Deserialize data to a Python object."""

    if not isinstance(data, dict) and not isinstance(data, list):  # type: ignore[unreachable]
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
    class_reference: type[T],
    data: Any,
    debug_name: str,
    *,
    throw_on_unhandled: bool,
    raw_storage_mode: RawStorageMode,
) -> T:
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

    def finalize(value: T) -> T:
        """Run through any finalization steps before returning the value."""

        # Set raw data where applicable
        if raw_storage_mode in [RawStorageMode.ROOT, RawStorageMode.ALL]:
            # We can't set attributes on primitive types
            if hasattr(value, "__dict__"):
                setattr(value, "__deserialize_raw__", data)

        return value

    if class_reference is Any:  # type: ignore[comparison-overlap]
        return cast(T, data)

    if inspect.isclass(class_reference) and issubclass(class_reference, CustomDeserializable):
        # If the class is a custom deserializable, we need to call the
        # deserialize method on it
        result = class_reference.deserialize(data)
        return finalize(cast(T, result))

    # Check if it's None (since things like Union[int, str | None] become
    # Union[int, str, None] so we end up iterating against it)
    if class_reference == type(None) and data is None:
        return cast(T, None)

    if is_union(class_reference):
        valid_types = union_types(class_reference, debug_name)
        exceptions: list[str] = []
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

    if not is_typing_type(class_reference) and issubclass(class_reference, enum.Enum):
        try:
            return finalize(class_reference(data))
        # pylint:disable=bare-except
        except:
            # pylint: disable=raise-missing-from
            raise DeserializeException(
                f"Cannot deserialize '{type(data)}' to '{class_reference}' for '{debug_name}'"
            )
        # pylint:enable=bare-except,raise-missing-from

    if isinstance(data, dict):
        return finalize(
            _deserialize_dict(
                class_reference,
                cast(dict[Any, Any], data),
                debug_name,
                throw_on_unhandled=throw_on_unhandled,
                raw_storage_mode=raw_storage_mode,
            )
        )

    if isinstance(data, list):
        return finalize(
            _deserialize_list(
                class_reference,
                cast(list[Any], data),
                debug_name,
                throw_on_unhandled=throw_on_unhandled,
                raw_storage_mode=raw_storage_mode,
            )
        )

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
    class_reference: type[T],
    list_data: list[Any],
    debug_name: str,
    *,
    throw_on_unhandled: bool,
    raw_storage_mode: RawStorageMode,
) -> T:
    if not is_list(class_reference):
        raise DeserializeException(
            f"Cannot deserialize a list to '{class_reference}' for {debug_name}"
        )

    if not isinstance(list_data, list):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise DeserializeException(
            f"Cannot deserialize '{type(list_data)}' as a list for {debug_name}."
        )

    list_content_type_value = list_content_type(class_reference, debug_name)

    output: list[Any] = []

    for index, item in enumerate(list_data):
        deserialized = _deserialize(
            list_content_type_value,
            item,
            f"{debug_name}[{index}]",
            throw_on_unhandled=throw_on_unhandled,
            raw_storage_mode=raw_storage_mode.child_mode(),
        )
        output.append(deserialized)

    return cast(T, output)


def _deserialize_dict(
    class_reference: type[T],
    data: dict[Any, Any],
    debug_name: str,
    *,
    throw_on_unhandled: bool,
    raw_storage_mode: RawStorageMode,
) -> T:
    """Deserialize a dictionary to a Python object."""

    # Check if we are doing a straightforward dictionary parse first, or if it
    # has to be deserialized

    remaining_properties = set(data.keys())

    if not isinstance(data, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise DeserializeException(
            f"Data was not dict for instance: {class_reference} for {debug_name}"
        )

    if is_dict(class_reference):
        if class_reference is dict:
            # If types of dictionary entries are not defined, do not deserialize
            return cast(T, data)
        key_type, value_type = dict_content_types(class_reference, debug_name)
        result: dict[Any, Any] = {}

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

        return cast(T, result)

    # It wasn't a straight forward dictionary, so we are in deserialize mode

    # Use metadata cache for performance
    metadata = get_class_metadata(class_reference)

    # Handle downcasting
    if metadata.downcast_field:
        downcast_value = data[metadata.downcast_field]
        new_reference = _get_downcast_class(class_reference, downcast_value)
        if new_reference is None:
            if metadata.allows_downcast_fallback:
                result_dict = _deserialize(
                    dict[Any, Any],
                    data,
                    debug_name,
                    throw_on_unhandled=throw_on_unhandled,
                    raw_storage_mode=raw_storage_mode.child_mode(),
                )
                return cast(T, result_dict)
            raise UndefinedDowncastException(
                f"Could not find subclass of {class_reference} with downcast identifier '{downcast_value}' for {debug_name}"
            )
        # Update class reference and get new metadata
        class_reference = cast(type[T], new_reference)
        metadata = get_class_metadata(class_reference)

    try:
        class_instance: T = class_reference.__new__(class_reference)
    except TypeError as ex:
        raise DeserializeException(
            f"Could not create instance of {class_reference} for {debug_name}"
        ) from ex

    handled_fields: set[str] = set()

    # Check if we have type hints (using cached hints from metadata)
    if len(metadata.hints) == 0:
        raise DeserializeException(
            f"Could not deserialize {data} into {class_reference} due to lack of type hints ({debug_name})"
        )

    # Process fields using cached metadata
    for attribute_name, field_meta in metadata.fields.items():
        # Skip ignored fields
        if field_meta.ignore:
            continue

        # Skip ClassVars
        if field_meta.is_classvar:
            if field_meta.key in data:
                raise DeserializeException(
                    f"ClassVars cannot be set: {debug_name}.{attribute_name}"
                )
            continue

        # Check auto_snake property naming
        if metadata.auto_snake and attribute_name.lower() != attribute_name:
            raise DeserializeException(
                f"When using auto_snake, all properties must be snake cased. Error on: {debug_name}.{attribute_name}"
            )

        using_default = False
        property_value: Any = None
        deserialized_value: Any = None

        # Look up value in data (using pre-computed keys for auto_snake)
        if field_meta.key in data:
            value = data[field_meta.key]
            handled_fields.add(field_meta.key)
            property_value = field_meta.parser(value)
        elif metadata.auto_snake and field_meta.camel_key and field_meta.camel_key in data:
            value = data[field_meta.camel_key]
            handled_fields.add(field_meta.camel_key)
            property_value = field_meta.parser(value)
        elif metadata.auto_snake and field_meta.pascal_key and field_meta.pascal_key in data:
            value = data[field_meta.pascal_key]
            handled_fields.add(field_meta.pascal_key)
            property_value = field_meta.parser(value)
        else:
            # Value not in data - check for default or None
            if field_meta.has_default:
                deserialized_value = field_meta.default_value
                using_default = True
            else:
                # Check if None is acceptable (Union with None)
                if (
                    field_meta.is_union
                    and field_meta.union_types
                    and type(None) in field_meta.union_types
                ):
                    property_value = field_meta.parser(None)
                else:
                    raise DeserializeException(
                        f"Unexpected missing value for: {debug_name}.{attribute_name}"
                    )

        if not using_default:
            deserialized_value = _deserialize(
                field_meta.type,
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

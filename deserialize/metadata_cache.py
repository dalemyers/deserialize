"""Class metadata caching for performance optimization."""

import typing
from typing import Any, Callable, get_args, get_origin, Annotated

from deserialize.decorators import (
    _get_key,
    _get_parser,
    _has_default,
    _get_default,
    _should_ignore,
    _uses_auto_snake,
    _get_downcast_field,
    _allows_downcast_fallback,
)
from deserialize.type_checks import (
    is_classvar,
    is_union,
    is_list,
    is_dict,
    union_types,
    list_content_type,
    dict_content_types,
)
from deserialize.conversions import camel_case, pascal_case
from deserialize.field import Field


def _extract_field_config(field_type: Any) -> tuple[Any, Field | None]:
    """Extract Field configuration from Annotated type hint.

    :param field_type: The type hint to inspect
    :returns: Tuple of (actual_type, field_config or None)
    """
    if get_origin(field_type) is Annotated:
        args = get_args(field_type)
        actual_type = args[0]  # First arg is the actual type

        # Look for Field in metadata
        for meta in args[1:]:
            if isinstance(meta, Field):
                return actual_type, meta

        return actual_type, None

    return field_type, None


class FieldMetadata:
    """Metadata for a single field."""

    __slots__ = (
        "name",
        "type",
        "key",
        "parser",
        "has_default",
        "default_value",
        "ignore",
        "is_classvar",
        "is_union",
        "is_list",
        "is_dict",
        "union_types",
        "list_type",
        "dict_key_type",
        "dict_value_type",
        "camel_key",
        "pascal_key",
    )

    name: str
    type: Any
    key: str
    parser: Callable[[Any], Any]
    has_default: bool
    default_value: Any
    ignore: bool
    is_classvar: bool
    is_union: bool
    is_list: bool
    is_dict: bool
    union_types: set[Any] | None
    list_type: Any | None
    dict_key_type: Any | None
    dict_value_type: Any | None
    camel_key: str | None
    pascal_key: str | None

    def __init__(
        self,
        name: str,
        field_type: Any,
        class_reference: Any,
        auto_snake: bool,
    ) -> None:
        self.name = name

        # Extract Field configuration from Annotated if present
        actual_type, field_config = _extract_field_config(field_type)
        self.type = actual_type

        # If Field is provided, it takes precedence over decorators
        if field_config:
            # Use Field configuration
            self.key = field_config.alias or name
            # Create a proper parser function
            if field_config.parser:
                self.parser = field_config.parser
            else:
                identity_func: Callable[[Any], Any] = lambda x: x
                self.parser = identity_func
            self.has_default = field_config.has_default()
            self.default_value = field_config.default if field_config.has_default() else None
            self.ignore = field_config.ignore
        else:
            # Fall back to decorator-based metadata
            self.key = _get_key(class_reference, name)
            self.parser = _get_parser(class_reference, self.key)
            self.has_default = _has_default(class_reference, name)
            self.default_value = _get_default(class_reference, name) if self.has_default else None
            self.ignore = _should_ignore(class_reference, name)

        # Type classification (use actual type, not Annotated wrapper)
        self.is_classvar = is_classvar(self.type)
        self.is_union = is_union(self.type)
        self.is_list = is_list(self.type)
        self.is_dict = is_dict(self.type)

        # Pre-computed type info
        self.union_types = None
        self.list_type = None
        self.dict_key_type = None
        self.dict_value_type = None

        if self.is_union:
            # Cache union types to avoid repeated get_args() calls
            self.union_types = union_types(self.type, f"metadata_{name}")

        if self.is_list:
            # Cache list content type
            self.list_type = list_content_type(self.type, f"metadata_{name}")

        if self.is_dict:
            # Cache dict types
            dict_types = dict_content_types(self.type, f"metadata_{name}")
            if dict_types:
                self.dict_key_type, self.dict_value_type = dict_types

        # Pre-compute auto-snake transformations
        self.camel_key = None
        self.pascal_key = None
        if auto_snake:
            self.camel_key = camel_case(self.key)
            self.pascal_key = pascal_case(self.key)


class ClassMetadata:
    """Cached metadata for a class."""

    __slots__ = (
        "class_reference",
        "hints",
        "fields",
        "auto_snake",
        "downcast_field",
        "allows_downcast_fallback",
    )

    class_reference: Any
    hints: dict[str, Any]
    fields: dict[str, FieldMetadata]
    auto_snake: bool
    downcast_field: str | None
    allows_downcast_fallback: bool

    def __init__(self, class_reference: Any):
        self.class_reference = class_reference

        # Get type hints once (include_extras=True to preserve Annotated metadata)
        self.hints = typing.get_type_hints(class_reference, include_extras=True)

        # Class-level decorators
        self.auto_snake = _uses_auto_snake(class_reference)
        self.downcast_field = _get_downcast_field(class_reference)
        self.allows_downcast_fallback = _allows_downcast_fallback(class_reference)

        # Build field metadata
        self.fields = {}
        for attr_name, attr_type in self.hints.items():
            self.fields[attr_name] = FieldMetadata(
                attr_name, attr_type, class_reference, self.auto_snake
            )


def get_class_metadata(class_reference: Any) -> ClassMetadata:
    """Get or create cached metadata for a class.

    :param class_reference: The class to get metadata for
    :returns: Cached ClassMetadata instance
    """
    cache_attr = "__deserialize_cache__"

    # Check if already cached (must be in class's own __dict__, not inherited)
    if hasattr(class_reference, "__dict__") and cache_attr in class_reference.__dict__:
        return class_reference.__dict__[cache_attr]

    # Create and cache metadata
    metadata = ClassMetadata(class_reference)

    # Only cache on classes that support attribute setting
    # Skip built-in immutable types
    try:
        if hasattr(class_reference, "__dict__"):
            setattr(class_reference, cache_attr, metadata)
    except (TypeError, AttributeError):
        # Can't cache on this type (e.g., built-in types like int, str)
        pass

    return metadata


def clear_class_cache(class_reference: Any) -> None:
    """Clear cached metadata for a class.

    This is useful if decorators are modified at runtime (not recommended).

    :param class_reference: The class to clear cache for
    """
    cache_attr = "__deserialize_cache__"
    if hasattr(class_reference, cache_attr):
        delattr(class_reference, cache_attr)

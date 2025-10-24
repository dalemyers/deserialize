"""Field configuration for type-hint based deserialization."""

from typing import Any, Callable, TypeVar


# Sentinel value to indicate no default was provided
_MISSING = object()

# Type variable for field values
_T = TypeVar("_T")


class Field:
    """Field configuration for deserialization using Annotated type hints.

    This provides an alternative to decorator-based configuration, allowing
    field metadata to be specified directly in type annotations.

    Example:
        from typing import Annotated
        from deserialize import Field, deserialize

        class User:
            user_id: Annotated[int, Field(alias="userId")]
            name: Annotated[str, Field(default="Unknown")]
            email: Annotated[str, Field(alias="emailAddress", parser=str.lower)]

    :param alias: Alternative key name in source data (replaces @key decorator)
    :param default: Default value if field is missing (replaces @default decorator)
    :param parser: Function to parse/transform the value (replaces @parser decorator)
    :param ignore: Whether to ignore this field during deserialization (replaces @ignore decorator)
    """

    __slots__ = ("alias", "default", "parser", "ignore", "_has_default")

    alias: str | None
    default: Any
    parser: Callable[[Any], Any] | None
    ignore: bool
    _has_default: bool

    def __init__(
        self,
        *,
        alias: str | None = None,
        default: Any = _MISSING,
        parser: Callable[[Any], Any] | None = None,
        ignore: bool = False,
    ) -> None:
        self.alias = alias
        self.default = default
        self.parser = parser
        self.ignore = ignore
        self._has_default = default is not _MISSING

    def has_default(self) -> bool:
        """Check if a default value was provided.

        :returns: True if default was set, False otherwise
        """
        return self._has_default

    def __repr__(self) -> str:
        parts: list[str] = []
        if self.alias is not None:
            parts.append(f"alias={self.alias!r}")
        if self._has_default:
            parts.append(f"default={self.default!r}")
        if self.parser is not None:
            parts.append(f"parser={self.parser!r}")
        if self.ignore:
            parts.append("ignore=True")
        return f"Field({', '.join(parts)})"

"""Decorators used for adding functionality to the library."""

from deserialize.decorators.constructed import constructed, _call_constructed
from deserialize.decorators.default import default, _get_default, _has_default
from deserialize.decorators.downcasting import (
    downcast_field,
    _get_downcast_field,
    downcast_identifier,
    _get_downcast_class,
    allow_downcast_fallback,
    _allows_downcast_fallback,
)
from deserialize.decorators.ignore import ignore, _should_ignore
from deserialize.decorators.key import key, _get_key
from deserialize.decorators.parser import parser, _get_parser
from deserialize.decorators.snake import auto_snake, _uses_auto_snake
from deserialize.decorators.unhandled import allow_unhandled, _should_allow_unhandled

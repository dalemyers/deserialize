"""Test exception handling and edge cases."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, DeserializeException
from deserialize import downcast_field, downcast_identifier
from deserialize import (
    InvalidBaseTypeException,
    UnhandledFieldException,
    UndefinedDowncastException,
)
from deserialize.decorators.default import _get_default, _has_default
from deserialize.exceptions import NoDefaultSpecifiedException

# pylint: enable=wrong-import-position


class SampleClass:
    """Sample class for testing."""

    value: int


def test_no_default_specified_exception() -> None:
    """Test that NoDefaultSpecifiedException is raised when default is not set."""

    # Test _has_default returns False for class without defaults
    assert not _has_default(SampleClass, "value")

    # Test _get_default raises NoDefaultSpecifiedException
    with pytest.raises(NoDefaultSpecifiedException):
        _get_default(SampleClass, "value")

    # Also test with a non-existent key
    with pytest.raises(NoDefaultSpecifiedException):
        _get_default(SampleClass, "non_existent")


def test_deserialize_exception_hierarchy() -> None:
    """Test that all custom exceptions inherit from DeserializeException."""
    # Test exception hierarchy
    assert issubclass(InvalidBaseTypeException, DeserializeException)
    assert issubclass(UnhandledFieldException, DeserializeException)
    assert issubclass(UndefinedDowncastException, DeserializeException)
    assert issubclass(NoDefaultSpecifiedException, DeserializeException)


def test_invalid_base_type_detailed() -> None:
    """Test InvalidBaseTypeException with various invalid base types."""
    invalid_types = [
        (42, int),
        ("string", str),
        (3.14, float),
        (True, bool),
        ({1, 2, 3}, set),
    ]

    for value, type_ref in invalid_types:
        with pytest.raises(InvalidBaseTypeException) as exc_info:
            deserialize(type_ref, value)

        assert "lists and dictionaries" in str(exc_info.value).lower()


def test_unhandled_field_exception_message() -> None:
    """Test UnhandledFieldException message format."""

    class StrictClass:
        """Class for strict testing."""

        value: int

    data = {"value": 1, "extra_field": "unexpected"}

    with pytest.raises(UnhandledFieldException) as exc_info:
        deserialize(StrictClass, data, throw_on_unhandled=True)

    error_message = str(exc_info.value)
    assert "extra_field" in error_message
    assert "unhandled" in error_message.lower()


def test_undefined_downcast_exception_message() -> None:
    """Test UndefinedDowncastException message format."""

    @downcast_field("type")
    class BaseClass:
        """Base class for downcasting."""

        type: str

    @downcast_identifier(BaseClass, "known")
    class _KnownClass(BaseClass):
        """Known subclass."""

        value: int

    data = {"type": "unknown", "value": 42}

    with pytest.raises(UndefinedDowncastException) as exc_info:
        deserialize(BaseClass, data)

    error_message = str(exc_info.value)
    assert "unknown" in error_message
    assert "BaseClass" in error_message or "downcast" in error_message.lower()

"""Decorators used for adding functionality to the library."""

from deserialize.exceptions import NoDefaultSpecifiedException
from deserialize.decorators import base


def default(key_name, default_value):
    """A decorator function for mapping default values to key names."""

    def store_defaults_map(class_reference):
        """Store the defaults map."""
        base.set_property(class_reference, "__deserialize_defaults_map__", key_name, default_value)
        return class_reference

    return store_defaults_map


def _has_default(class_reference, key_name):
    """Returns True if this key has a default, False otherwise.

    :returns: True if this key has a default, False otherwise.
    """

    sentinel = object()

    default_value = base.get_property(
        class_reference, "__deserialize_defaults_map__", key_name, sentinel
    )

    return default_value != sentinel


def _get_default(class_reference, key_name):
    """Get the default value for the given class and key name.

    :raises NoDefaultSpecifiedException: If a default hasn't been specified
    """

    sentinel = object()

    default_value = base.get_property(
        class_reference, "__deserialize_defaults_map__", key_name, sentinel
    )

    if default_value != sentinel:
        return default_value

    raise NoDefaultSpecifiedException()

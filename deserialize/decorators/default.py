"""Decorators used for adding functionality to the library."""

from deserialize.exceptions import NoDefaultSpecifiedException


def default(key_name, default_value):
    """A decorator function for mapping default values to key names."""

    def store_defaults_map(class_reference):
        """Store the defaults map."""

        if not hasattr(class_reference, "__deserialize_defaults_map__"):
            setattr(class_reference, "__deserialize_defaults_map__", {})

        class_reference.__deserialize_defaults_map__[key_name] = default_value

        return class_reference

    return store_defaults_map


def _has_default(class_reference, key_name):
    """Returns True if this key has a default, False otherwise.

    :returns: True if this key has a default, False otherwise.
    """

    if not hasattr(class_reference, "__deserialize_defaults_map__"):
        return False

    return key_name in class_reference.__deserialize_defaults_map__


def _get_default(class_reference, key_name):
    """Get the default value for the given class and key name.

    :raises NoDefaultSpecifiedException: If a default hasn't been specified
    """

    if not hasattr(class_reference, "__deserialize_defaults_map__"):
        raise NoDefaultSpecifiedException()

    if key_name in class_reference.__deserialize_defaults_map__:
        return class_reference.__deserialize_defaults_map__[key_name]

    raise NoDefaultSpecifiedException()

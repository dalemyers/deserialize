"""Decorators used for adding functionality to the library."""

from deserialize.exceptions import NoDefaultSpecifiedException


def ignore(property_name):
    """A decorator function for marking keys as those which should be ignored."""

    def store_key_map(class_reference):
        """Store the key map."""
        if not hasattr(class_reference, "__deserialize_ignore_map__"):
            setattr(class_reference, "__deserialize_ignore_map__", {})

        class_reference.__deserialize_ignore_map__[property_name] = True

        return class_reference

    return store_key_map


def _should_ignore(class_reference, property_name):
    """Check if a property should be ignored."""

    if not hasattr(class_reference, "__deserialize_ignore_map__"):
        return False

    return class_reference.__deserialize_ignore_map__.get(property_name, False)


def key(property_name, key_name):
    """A decorator function for mapping key names to properties."""

    def store_key_map(class_reference):
        """Store the key map."""
        if not hasattr(class_reference, "__deserialize_key_map__"):
            setattr(class_reference, "__deserialize_key_map__", {})

        class_reference.__deserialize_key_map__[property_name] = key_name

        return class_reference

    return store_key_map


def _get_key(class_reference, property_name):
    """Get the key for the given class and property name."""

    if not hasattr(class_reference, "__deserialize_key_map__"):
        return property_name

    return class_reference.__deserialize_key_map__.get(property_name, property_name)


def parser(key_name, parser_function):
    """A decorator function for mapping parsers to key names."""

    def store_parser_map(class_reference):
        """Store the parser map."""

        if not hasattr(class_reference, "__deserialize_parser_map__"):
            setattr(class_reference, "__deserialize_parser_map__", {})

        class_reference.__deserialize_parser_map__[key_name] = parser_function

        return class_reference

    return store_parser_map


def _get_parser(class_reference, key_name):
    """Get the parser for the given class and key name."""

    def identity_parser(value):
        """This parser does nothing. It's simply used as the default."""
        return value

    if not hasattr(class_reference, "__deserialize_parser_map__"):
        return identity_parser

    return class_reference.__deserialize_parser_map__.get(key_name, identity_parser)


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

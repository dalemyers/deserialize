"""Decorators used for adding functionality to the library."""

from deserialize.decorators import base


def _identity_parser(value):
    """This parser does nothing. It's simply used as the default."""
    return value


def parser(key_name, parser_function):
    """A decorator function for mapping parsers to key names."""

    def store_parser_map(class_reference):
        """Store the parser map."""
        base.set_property(class_reference, "__deserialize_parser_map__", key_name, parser_function)
        return class_reference

    return store_parser_map


def _get_parser(class_reference, key_name):
    """Get the parser for the given class and key name."""
    return base.get_property(
        class_reference, "__deserialize_parser_map__", key_name, _identity_parser
    )

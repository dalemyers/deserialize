"""Decorators used for adding functionality to the library."""

from deserialize.decorators import base


def ignore(property_name):
    """A decorator function for marking keys as those which should be ignored."""

    def store_key_map(class_reference):
        """Store the key map."""
        base.set_property(class_reference, "__deserialize_ignore_map__", property_name, True)
        return class_reference

    return store_key_map


def _should_ignore(class_reference, property_name):
    """Check if a property should be ignored."""
    return base.get_property(class_reference, "__deserialize_ignore_map__", property_name, False)

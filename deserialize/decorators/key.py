"""Decorators used for adding functionality to the library."""


from deserialize.decorators import base


def key(property_name, key_name):
    """A decorator function for mapping key names to properties."""

    def store_key_map(class_reference):
        """Store the key map."""
        base.set_property(class_reference, "__deserialize_key_map__", property_name, key_name)
        return class_reference

    return store_key_map


def _get_key(class_reference, property_name):
    """Get the key for the given class and property name."""

    return base.get_property(
        class_reference, "__deserialize_key_map__", property_name, property_name
    )

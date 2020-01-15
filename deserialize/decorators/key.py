"""Decorators used for adding functionality to the library."""


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

"""Decorators used for adding functionality to the library."""


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

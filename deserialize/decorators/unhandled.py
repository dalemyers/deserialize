"""Decorators used for adding functionality to the library."""


def allow_unhandled(key_name):
    """A decorator function for marking keys as allowed to be unhandled."""

    def store_allow_unhandled_map(class_reference):
        """Store the key map."""
        if not hasattr(class_reference, "__deserialize_allow_unhandled_map__"):
            setattr(class_reference, "__deserialize_allow_unhandled_map__", {})

        class_reference.__deserialize_allow_unhandled_map__[key_name] = True

        return class_reference

    return store_allow_unhandled_map


def _should_allow_unhandled(class_reference, key_name):
    """Check if a property is allowed to be unhandled."""

    if not hasattr(class_reference, "__deserialize_allow_unhandled_map__"):
        return False

    return class_reference.__deserialize_allow_unhandled_map__.get(key_name, False)

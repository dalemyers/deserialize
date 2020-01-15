"""Decorators used for adding functionality to the library."""


def downcast_field(property_name):
    """A decorator function for handling downcasting."""

    def store_downcast_field_value(class_reference):
        """Store the key map."""
        setattr(class_reference, "__deserialize_downcast_field__", property_name)
        return class_reference

    return store_downcast_field_value


def _get_downcast_field(class_reference):
    """Get the downcast field name if set, None otherwise."""
    return getattr(class_reference, "__deserialize_downcast_field__", None)


def downcast_identifier(super_class, identifier):
    """A decorator function for storing downcast identifiers."""

    def store_key_map(class_reference):
        """Store the downcast map."""
        if not hasattr(class_reference, "__deserialize_downcast_map__"):
            setattr(class_reference, "__deserialize_downcast_map__", {})

        class_reference.__deserialize_downcast_map__[super_class] = identifier

        return class_reference

    return store_key_map


def _get_downcast_identifier(class_reference, super_class):
    """Get the downcast identifier for the given class and super class, returning None if not set"""

    if not hasattr(class_reference, "__deserialize_downcast_map__"):
        return None

    return class_reference.__deserialize_downcast_map__.get(super_class)

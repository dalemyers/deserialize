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
        if not hasattr(super_class, "__deserialize_downcast_map__"):
            setattr(super_class, "__deserialize_downcast_map__", {})

        super_class.__deserialize_downcast_map__[identifier] = class_reference

        return class_reference

    return store_key_map


def _get_downcast_class(super_class, identifier):
    """Get the downcast identifier for the given class and super class, returning None if not set"""

    if not hasattr(super_class, "__deserialize_downcast_map__"):
        return None

    return super_class.__deserialize_downcast_map__.get(identifier)


def allow_downcast_fallback():
    """A decorator function for setting that downcast fallback to dicts is allowed."""

    def store(class_reference):
        """Store the allowance flag."""
        setattr(class_reference, "__deserialize_downcast_allow_fallback__", True)
        return class_reference

    return store


def _allows_downcast_fallback(super_class):
    """Get the whether downcast can fallback to a dict or not"""
    return getattr(super_class, "__deserialize_downcast_allow_fallback__", False)

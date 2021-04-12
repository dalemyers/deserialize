"""Decorators used for adding functionality to the library."""

from deserialize.decorators import base


def downcast_field(property_name):
    """A decorator function for handling downcasting."""

    def store_downcast_field_value(class_reference):
        """Store the key map."""
        base.set_property(class_reference, "__deserialize_downcast_field__", "value", property_name)
        return class_reference

    return store_downcast_field_value


def _get_downcast_field(class_reference):
    """Get the downcast field name if set, None otherwise."""
    return base.get_property(class_reference, "__deserialize_downcast_field__", "value")


def downcast_identifier(super_class, identifier):
    """A decorator function for storing downcast identifiers."""

    def store_key_map(class_reference):
        """Store the downcast map."""
        base.set_property(super_class, "__deserialize_downcast_map__", identifier, class_reference)
        return class_reference

    return store_key_map


def _get_downcast_class(super_class, identifier):
    """Get the downcast identifier for the given class and super class, returning None if not set"""
    return base.get_property(super_class, "__deserialize_downcast_map__", identifier)


def allow_downcast_fallback():
    """A decorator function for setting that downcast fallback to dicts is allowed."""

    def store(class_reference):
        """Store the allowance flag."""
        base.set_property(class_reference, "__deserialize_downcast_allow_fallback__", "value", True)
        return class_reference

    return store


def _allows_downcast_fallback(super_class):
    """Get the whether downcast can fallback to a dict or not"""
    return base.get_property(super_class, "__deserialize_downcast_allow_fallback__", "value", False)

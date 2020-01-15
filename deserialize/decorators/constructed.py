"""Decorators used for adding functionality to the library."""


def constructed(function):
    """A decorator function for calling when a class is constructed."""

    def store_constructed(class_reference):
        """Store the key map."""
        setattr(class_reference, "__deserialize_constructed__", function)
        return class_reference

    return store_constructed


def _call_constructed(class_reference, instance):
    """Check if a property is allowed to be unhandled."""

    if not hasattr(class_reference, "__deserialize_constructed__"):
        return

    class_reference.__deserialize_constructed__(instance)

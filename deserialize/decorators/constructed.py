"""Decorators used for adding functionality to the library."""

from deserialize.decorators import base


def constructed(function):
    """A decorator function for calling when a class is constructed."""

    def store_constructed(class_reference):
        """Store the key map."""
        base.set_property(class_reference, "__deserialize_constructed__", "constructed", function)
        return class_reference

    return store_constructed


def _call_constructed(class_reference, instance):
    """Check if a property is allowed to be unhandled."""

    constructor = base.get_property(class_reference, "__deserialize_constructed__", "constructed")
    if constructor:
        constructor(instance)

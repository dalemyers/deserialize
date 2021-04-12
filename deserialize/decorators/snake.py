"""Decorators used for adding functionality to the library."""

from deserialize.decorators import base


def auto_snake():
    """A decorator function for marking classes as those which should be auto-snaked."""

    def store(class_reference):
        """Store the allowance flag."""
        base.set_property(class_reference, "__deserialize_auto_snake__", "value", True)
        return class_reference

    return store


def _uses_auto_snake(class_reference):
    """Get the whether auto-snake is in use or not"""
    return base.get_property(class_reference, "__deserialize_auto_snake__", "value", False)

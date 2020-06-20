"""Decorators used for adding functionality to the library."""


def auto_snake():
    """A decorator function for marking classes as those which should be auto-snaked."""

    def store(class_reference):
        """Store the allowance flag."""
        setattr(class_reference, "__deserialize_auto_snake__", True)
        return class_reference

    return store


def _uses_auto_snake(super_class):
    """Get the whether auto-snake is in use or not"""
    return getattr(super_class, "__deserialize_auto_snake__", False)

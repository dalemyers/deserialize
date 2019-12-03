"""Module for all exceptions used in the library."""


class DeserializeException(Exception):
    """Represents an error deserializing a value."""


class InvalidBaseTypeException(DeserializeException):
    """An error where the "base" type to be deserialized was invalid."""


class UnhandledFieldException(DeserializeException):
    """An error thrown when a field is unhandled."""

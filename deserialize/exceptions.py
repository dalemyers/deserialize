"""Module for all exceptions used in the library."""


class DeserializeException(Exception):
    """Represents an error deserializing a value."""


class InvalidBaseTypeException(DeserializeException):
    """An error where the "base" type to be deserialized was invalid."""


class UnhandledFieldException(DeserializeException):
    """An error thrown when a field is unhandled."""


class NoDefaultSpecifiedException(DeserializeException):
    """An error thrown when we try and get a default but one has not been specified.

    This is required to differentiate from None as a default value.
    """


class UndefinedDowncastException(DeserializeException):
    """The data required a downcast to a specific type, but that type has not been defined.

    This can be an expected scenario though for many cases.
    """

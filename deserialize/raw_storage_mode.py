"""A module for deserializing data to Python objects."""

# pylint: disable=unidiomatic-typecheck
# pylint: disable=protected-access
# pylint: disable=too-many-branches
# pylint: disable=wildcard-import

import enum

from .exceptions import DeserializeException


class RawStorageMode(enum.Enum):
    """The storage mode for the raw data on each object.

    If a store mode is set, the data will be stored in the attribute named:
    `__deserialize_raw__`
    """

    # Do not store the raw data at all
    NONE = "none"

    # Only store the data on the root node
    ROOT = "root"

    # Store on all objects (WARNING: This can use a significant amount of memory)
    ALL = "all"

    def child_mode(self) -> "RawStorageMode":
        """Determine the mode for child parsing.

        When we move to the next child iteration, we need to change mode
        in some cases. For instance, if we only store the root node, then we
        need to set all the children to not be stored.

        :raises Exception: If we get an unexpected storage mode

        :returns: The child raw storage mode
        """
        if self == RawStorageMode.NONE:
            return RawStorageMode.NONE

        if self == RawStorageMode.ROOT:
            return RawStorageMode.NONE

        if self == RawStorageMode.ALL:
            return RawStorageMode.ALL

        raise DeserializeException(f"Unexpected raw storage mode: {self}")

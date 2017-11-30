"""Defines the common orb-framework exception types."""


class OrbException(Exception):
    """Base exception class."""

    pass


class ReadOnly(OrbException):
    """Raised when a read-only variable is attempting to be modified."""

    def __init__(self, name: str):
        super().__init__('{} are read only'.format(name))


class StoreNotFound(OrbException):
    """Raised when accessing a store but none is available."""

    def __init__(self):
        super().__init__('Store not found.')

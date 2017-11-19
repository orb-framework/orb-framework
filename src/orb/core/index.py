"""Define Index class."""
from enum import IntFlag, auto


class IndexFlags(IntFlag):
    """Flags for the Index class."""

    Virtual = auto()


class Index:
    """Class to identify lookups."""

    Flags = IndexFlags

    def __init__(
        self,
        *,
        code: str=None,
        flags: IndexFlags=IndexFlags(0),
        name: str=None,
    ):
        self.code = code
        self.name = name

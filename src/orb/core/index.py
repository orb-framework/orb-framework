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
        gettermethod: callable=None,
        name: str=None,
        querymethod: callable=None,
        settermethod: callable=None,
    ):
        self.code = code
        self.name = name
        self.gettermethod = gettermethod
        self.querymethod = querymethod
        self.settermethod = settermethod

    def getter(self, func: callable) -> callable:
        """Assign gettermethod via decorator."""
        self.gettermethod = func
        return func

    def query(self, func: callable) -> callable:
        """Assign querymethod via decorator."""
        self.querymethod = func
        return func

    def setter(self, func: callable) -> callable:
        """Assign settermethod via decorator."""
        self.settermethod = func
        return func

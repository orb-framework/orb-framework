"""Define Index class."""

from aenum import IntFlag, auto

from typing import Union

from ..utils import enum_from_set


class IndexFlags(IntFlag):
    """Flags for the Index class."""

    Key = auto()
    Unique = auto()
    Virtual = auto()


class Index:
    """Class to identify lookups."""

    Flags = IndexFlags

    def __init__(
        self,
        field_names=[],
        code: str='',
        flags: Union[IndexFlags, set]=IndexFlags(0),
        name: str=''
    ):
        self.code = code
        self.name = name
        self.field_names = field_names
        self.flags = (
            enum_from_set(IndexFlags, flags)
            if type(flags) is set else flags
        )

    def test_flag(self, flag: IndexFlags) -> bool:
        """Test if this index has the given flag."""
        return bool(self.flags & flag)

"""Define Field class."""

import re
from enum import IntFlag, auto
from typing import Any

from ..utils import enum_from_set


class FieldFlags(IntFlag):
    """Flag options for fields."""

    AutoAssign = auto()
    AutoInclude = auto()
    CaseSensitive = auto()
    Encrypted = auto()
    Keyable = auto()
    Polymorph = auto()
    Protected = auto()
    Private = auto()
    Required = auto()
    RequiresInclude = auto()
    ReadOnly = auto()
    Searchable = auto()
    Static = auto()
    Translatable = auto()
    Unique = auto()
    Virtual = auto()


class Field:
    """Data class type for models."""

    Flags = FieldFlags

    def __init__(
        self,
        *,
        code: str=None,
        default: Any=None,
        flags: Flags=FieldFlags(0),
        gettermethod: callable=None,
        label: str='',
        name: str='',
        querymethod: callable=None,
        settermethod: callable=None,
        shortcut: str='',
    ):
        self._code = code
        self._default = default
        self.flags = (
            enum_from_set(FieldFlags, flags)
            if type(flags) is set else flags
        )
        self.gettermethod = gettermethod
        self._label = label
        self.name = name
        self.querymethod = querymethod
        self.settermethod = settermethod
        self.shortcut = shortcut

    def get_code(self) -> str:
        """Return code for this field.

        If no code is defined, then the name will
        be used.  The code will be used as the
        backend identifier.
        """
        if callable(self._code):
            return self._code(self)
        return self._code or self.name

    def get_default(self) -> Any:
        """Return default value for this field."""
        if callable(self._default):
            return self._default(self)
        return self._default

    def get_label(self) -> str:
        """Return display text label.

        If no label is defined, then a titlized
        version of the name will be returned.
        """
        if self._label:
            return self._label
        text = ' '.join(re.findall('[a-zA-Z0-9]+', self.name))
        return text.title()

    def getter(self, func: callable) -> callable:
        """Set the gettermethod property via decorator."""
        self.gettermethod = func
        return func

    def set_code(self, code: str):
        """Set code for this field."""
        self._code = code

    def set_default(self, default: Any):
        """Set the default value for this field."""
        self._default = default

    def set_label(self, label: str):
        """Set display text label."""
        self._label = label

    def query(self, func: callable) -> callable:
        """Set the querymethod property via decorator."""
        self.querymethod = func
        return func

    def setter(self, func: callable) -> callable:
        """Set the settermethod property via decorator."""
        self.settermethod = func
        return func

    def test_flag(self, flag: Flags) -> bool:
        """Test to see if this field has the given flag."""
        return bool(self.flags & flag)

    code = property(get_code, set_code)
    default = property(get_default, set_default)
    label = property(get_label, set_label)

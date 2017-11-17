"""Define Field class."""

import re
from enum import Flag, auto
from typing import Any


class Flags(Flag):
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

    Flags = Flags

    def __init__(
        self,
        *,
        code: str='',
        default: Any=None,
        flags: Flags=Flags(0),
        gettermethod: callable=None,
        label: str='',
        name: str='',
        querymethod: callable=None,
        settermethod: callable=None,
        shortcut: str='',
    ):
        self._code = code
        self._default = default
        self.flags = flags
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
        return self._code or self.make_code(self.name)

    def get_default(self) -> Any:
        """Return default value for this field."""
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

    def make_code(self, name: str) -> str:
        """Generate code from name."""
        return name

    def set_code(self, code: str):
        """Set code for this field."""
        self._code = code

    def set_default(self, default: Any):
        """Set the default value for this field."""
        self._default = default

    def set_label(self, label: str):
        """Set display text label."""
        self._label = label

    def querymethod(self, func: callable) -> callable:
        """Set the querymethod property via decorator."""
        self.gettermethod = func
        return func

    def settermethod(self, func: callable) -> callable:
        """Set the settermethod property via decorator."""
        self.gettermethod = func
        return func

    def test_flag(self, flag: Flags) -> bool:
        """Test to see if this field has the given flag."""
        return bool(self.flags & flag)

    code = property(get_code, set_code)
    default = property(get_default)
    label = property(get_label, set_label)

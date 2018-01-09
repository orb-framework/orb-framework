"""Define Field class."""

import inflection

from aenum import IntFlag, auto

from typing import Any, Type, Union

from .context import Ordering
from ..utils import enum_from_set


class FieldFlags(IntFlag):
    """Flag options for fields."""

    AutoAssign = auto()
    AutoInclude = auto()
    CaseSensitive = auto()
    Encrypted = auto()
    Key = auto()
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
        default_ordering: Ordering=Ordering.Asc,
        flags: Union[FieldFlags, set]=FieldFlags(0),
        gettermethod: callable=None,
        label: str='',
        name: str='',
        querymethod: callable=None,
        refers_to: str=None,
        settermethod: callable=None,
        shortcut: str=''
    ):
        self.default_ordering = default_ordering
        self.flags = (
            enum_from_set(FieldFlags, flags)
            if type(flags) is set else flags
        )
        self.gettermethod = gettermethod
        self.name = name
        self.querymethod = querymethod
        self.refers_to = refers_to
        self.settermethod = settermethod
        self.shortcut = shortcut

        self._code = code
        self._default = default
        self._label = label

    def __lt__(self, other) -> int:
        """Compare one field to another for sorting."""
        if type(other) is Field:
            return self.name < other.name
        return True

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
        return inflection.titleize(self.name)

    def getter(self, func: callable) -> callable:
        """Set the gettermethod property via decorator."""
        self.gettermethod = func
        return func

    def get_refers_to_field(self) -> 'Field':
        """Return the remote field this instance refers to, if any."""
        model = self.refers_to_model
        if model:
            _, field_name = self.refers_to.split('.', 1)
            return model.__schema__.fields[field_name]
        return None

    def get_refers_to_model(self) -> Type['Model']:
        """Return the model this field refers to, if any."""
        if self.refers_to:
            from .model import Model
            model_name, _ = self.refers_to.split('.', 1)
            return Model.find_model(model_name)
        return None

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
    refers_to_model = property(get_refers_to_model)
    refers_to_field = property(get_refers_to_field)

"""Define Query class type."""

from enum import Enum
from typing import Any


class Op(Enum):
    """Query operators."""

    Is = 'is'
    IsNot = 'is_not'


class Query:
    """Python query language builder."""

    Op = Op

    def __init__(
        self,
        name: str='',
        op: Op=Op.Is,
        value: Any=None,
    ):
        self.name = name
        self.op = op
        self.value = value

    def __eq__(self, other):
        """Set op to Is and value to other."""
        return self.clone({'op': Query.Op.Is, 'value': other})

    def __ne__(self, other):
        """Set op to IsNot and value to other."""
        return self.clone({'op': Query.Op.IsNot, 'value': other})

    def clone(self, values: dict=None):
        """Copy current query and return new object."""
        defaults = {
            'name': self.name,
            'op': self.op,
            'value': self.value,
        }
        defaults.update(values or {})
        return type(self)(**defaults)

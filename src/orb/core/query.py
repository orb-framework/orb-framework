"""Define Query class type."""

from enum import Enum
from typing import Any

from .query_group import QueryGroup


class QueryOp(Enum):
    """Query operators."""

    Is = 'is'
    IsNot = 'is_not'


class Query:
    """Python query language builder."""

    Op = QueryOp

    def __init__(
        self,
        name: str='',
        model: str='',
        op: QueryOp=QueryOp.Is,
        value: Any=None,
    ):
        self.model = model
        self.name = name
        self.op = op
        self.value = value

    def __and__(self, other):
        """Join query with another."""
        if not (self.is_null or getattr(other, 'is_null', False)):
            return QueryGroup(
                op=QueryGroup.Op.And,
                queries=[self, other],
            )
        elif not getattr(other, 'is_null', False):
            return other
        return self

    def __or__(self, other):
        """Join query with another."""
        if not (self.is_null or getattr(other, 'is_null', False)):
            return QueryGroup(
                op=QueryGroup.Op.Or,
                queries=[self, other],
            )
        elif not getattr(other, 'is_null', False):
            return other
        return self

    def __eq__(self, other):
        """Set op to Is and value to other."""
        return self.clone({'op': QueryOp.Is, 'value': other})

    def __ne__(self, other):
        """Set op to IsNot and value to other."""
        return self.clone({'op': QueryOp.IsNot, 'value': other})

    def clone(self, values: dict=None):
        """Copy current query and return new object."""
        defaults = {
            'name': self.name,
            'op': self.op,
            'value': self.value,
        }
        defaults.update(values or {})
        return type(self)(**defaults)

    @property
    def is_null(self) -> bool:
        """Return whether or not this query object is null."""
        return not(self.name or self.model)

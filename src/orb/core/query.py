"""Define Query class type."""

from enum import Enum
from typing import Any, Union


class QueryOp(Enum):
    """Query operators."""

    After = 'after'
    Before = 'before'
    Between = 'between'
    Contains = 'contains'
    ContainsInsensitive = 'contains_insensitive'
    DoesNotMatch = 'does_not_match'
    DoesNotStartwith = 'does_not_start_with'
    DoesNotEndWith = 'does_not_end_with'
    Endswith = 'endswith'
    Is = 'is'
    IsIn = 'is_in'
    IsNot = 'is_not'
    IsNotIn = 'is_not_in'
    GreaterThan = 'greater_than'
    GreaterThanOrEqual = 'greater_than_or_equal'
    LessThan = 'less_than'
    LessThanOrEqual = 'less_than_or_equal'
    Matches = 'matches'
    Startswith = 'startswith'


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

    def __and__(
        self,
        other: Union['Query', 'QueryGroup'],
    ) -> Union['Query', 'QueryGroup']:
        """Join query with another."""
        from .query_group import make_query_group, QueryGroupOp
        return make_query_group(self, other, QueryGroupOp.And)

    def __eq__(self, other: Any) -> 'Query':
        """Set op to Is and value to other."""
        return self.clone({'op': QueryOp.Is, 'value': other})

    def __ne__(self, other: Any) -> 'Query':
        """Set op to IsNot and value to other."""
        return self.clone({'op': QueryOp.IsNot, 'value': other})

    def __or__(
        self,
        other: Union['Query', 'QueryGroup'],
    ) -> Union['Query', 'QueryGroup']:
        """Join query with another."""
        from .query_group import make_query_group, QueryGroupOp
        return make_query_group(self, other, QueryGroupOp.Or)

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

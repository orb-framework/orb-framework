"""Define Query class type."""

from enum import Enum
from typing import Any, Type, Union


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
        *args,
        name: str='',
        model: Union[str, Type['Model']]='',
        op: QueryOp=QueryOp.Is,
        value: Any=None
    ):
        if len(args) == 1:
            arg = args[0]
            if type(arg) is tuple:
                model, name = arg
            else:
                name = arg
        elif len(args) > 1:
            msg = 'Query() takes 0-1 positional arguments but {} was given'
            raise TypeError(msg.format(len(args)))

        self._model = model
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
            'model': self._model,
            'name': self.name,
            'op': self.op,
            'value': self.value,
        }
        defaults.update(values or {})
        return type(self)(**defaults)

    def get_model(self) -> Type['Model']:
        """Return model type associated with this query, if any."""
        if type(self._model) is str:
            from .model import Model
            return Model.find_model(self._model)
        return self._model

    @property
    def is_null(self) -> bool:
        """Return whether or not this query object is null."""
        return not(self.name or self.model)

    def set_model(self, model: Union[str, Type['Model']]):
        """Set model type instance for this query."""
        self._model = model

    model = property(get_model, set_model)

"""Define QueryGroup class."""
from enum import Enum


class QueryGroupOp(Enum):
    """Define QueryGroupOp class type."""

    And = 'and'
    Or = 'or'


class QueryGroup:
    """Define QueryGroup class type."""

    Op = QueryGroupOp

    def __init__(
        self,
        *,
        op: QueryGroupOp=QueryGroupOp.And,
        queries: list=None
    ):
        self.op = op
        self.queries = queries

    def __and__(self, other):
        """Merge other query with this one."""
        if not (self.is_null or other.is_null):
            if other.op == QueryGroupOp.And:
                if isinstance(other, QueryGroup):
                    queries = self.queries + other.queries
                else:
                    queries = self.queries + [other]

                return QueryGroup(
                    op=QueryGroupOp.And,
                    queries=queries
                )
            return QueryGroup(
                op=QueryGroupOp.And,
                queries=[self, other]
            )
        elif not other.is_null:
            return other
        return self

    def __or__(self, other):
        """Merge other query with this one."""
        if not (self.is_null or other.is_null):
            if other.op == QueryGroupOp.Or:
                if isinstance(other, QueryGroup):
                    queries = self.queries + other.queries
                else:
                    queries = self.queries + [other]

                return QueryGroup(
                    op=QueryGroupOp.Or,
                    queries=queries
                )
            return QueryGroup(
                op=QueryGroupOp.Or,
                queries=[self, other]
            )
        elif not other.is_null:
            return other
        return self

    @property
    def is_null(self):
        """Return whether or not this group is empty."""
        return len(self.queries) == 0

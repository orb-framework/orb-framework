"""Define QueryGroup class."""
from enum import Enum
from typing import Union


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
        return make_query_group(self, other, QueryGroup.Op.And)

    def __or__(self, other):
        """Merge other query with this one."""
        return make_query_group(self, other, QueryGroup.Op.Or)

    @property
    def is_null(self):
        """Return whether or not this group is empty."""
        return len(self.queries) == 0


def make_query_group(
    left: Union['Query', QueryGroup],
    right: Union['Query', QueryGroup],
    op: QueryGroupOp
):
    """Create new query group by joining the left and right queries."""
    is_left_group = isinstance(left, QueryGroup)
    is_right_group = isinstance(right, QueryGroup)

    if getattr(right, 'is_null', True):
        return left
    elif getattr(left, 'is_null', True):
        return right
    elif is_left_group and is_right_group and left.op == right.op == op:
        return QueryGroup(
            op=op,
            queries=left.queries + right.queries
        )
    elif is_left_group and left.op == op:
        return QueryGroup(
            op=op,
            queries=left.queries + [right]
        )
    elif is_right_group and right.op == op:
        return QueryGroup(
            op=op,
            queries=[left] + right.queries
        )

    return QueryGroup(
        op=op,
        queries=[left, right]
    )

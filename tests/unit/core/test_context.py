"""Tests for the Context class."""


def test_context_creation():
    """Test creating an empty context."""
    from orb import make_context, ReturnType

    context = make_context()
    assert context.distinct is None
    assert context.fields is None
    assert context.locale is None
    assert context.limit is None
    assert context.namespace is None
    assert context.ordering is None
    assert context.page is None
    assert context.page_size is None
    assert context.query is None
    assert context.returning is ReturnType.Records
    assert context.scope == {}
    assert context.start is None
    assert context.timezone is None


def test_context_merging():
    """Test merging two contexts together."""
    from orb import (
        make_context,
        Query as Q,
        QueryGroup,
        Ordering,
    )

    a = make_context(
        fields='a,b',
        ordering='+a,-b',
        query=Q('a') == 1,
        scope={'a': 1}
    )
    b = make_context(
        context=a,
        fields=['b', 'c', 'd'],
        query=Q('b') != 1,
        scope={'b': 2}
    )

    assert b.ordering == [('a', Ordering.Asc), ('b', Ordering.Desc)]
    assert b.fields == ['b', 'c', 'd', 'a']
    assert b.scope == {'a': 1, 'b': 2}
    assert type(b.query) == QueryGroup
    assert len(b.query.queries) == 2

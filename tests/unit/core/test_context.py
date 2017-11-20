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
    assert context.order is None
    assert context.page is None
    assert context.page_size is None
    assert context.where is None
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
        distinct='a',
        fields='a,b',
        locale='en_US',
        limit=5,
        order='+a,-b',
        scope={'a': 1},
        where=Q('a') == 1,
    )
    b = make_context(
        context=a,
        distinct='b',
        fields=['b', 'c', 'd'],
        locale='fr_FR',
        limit=None,
        scope={'b': 2},
        where=Q('b') != 1,
    )

    assert b.order == [('a', Ordering.Asc), ('b', Ordering.Desc)]
    assert b.fields == ['b', 'c', 'd', 'a']
    assert b.scope == {'a': 1, 'b': 2}
    assert type(b.where) == QueryGroup
    assert len(b.where.queries) == 2
    assert b.distinct == ['b']
    assert b.locale == 'fr_FR'
    assert b.limit is None


def test_context_limiting():
    """Test basic context limiting options."""
    from orb import make_context

    context = make_context(start=10, limit=10)
    assert context.page is None
    assert context.page_size is None
    assert context.start == 10
    assert context.limit == 10

    context.start = 20
    context.limit = 20

    assert context.start == 20
    assert context.limit == 20


def test_context_page_limiting():
    """Test page based context limiting options."""
    from orb import make_context

    context = make_context(
        page=2,
        page_size=100
    )

    assert context.page == 2
    assert context.page_size == 100
    assert context.start == 100
    assert context.limit == 100

    context.start = 20
    context.limit = 20

    assert context.start == 100
    assert context.limit == 100

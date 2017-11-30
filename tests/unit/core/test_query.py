"""Tests for the Query class."""


def test_query_initialization():
    """Test basic query initialization."""
    from orb import Query as Q

    q = Q('username')
    assert q.name == 'username'
    assert q.op is Q.Op.Is
    assert q.value is None


def test_query_equals():
    """Test query equals operator."""
    from orb import Query as Q

    q = Q('username') == 'bob'
    assert q.name == 'username'
    assert q.op == Q.Op.Is
    assert q.value == 'bob'


def test_query_not_equals():
    """Test query not-equals operator."""
    from orb import Query as Q

    q = Q('username') != 'bob'
    assert q.name == 'username'
    assert q.op == Q.Op.IsNot
    assert q.value == 'bob'


def test_query_and_joining_two_query_objects():
    """Test AND joining two query objects."""
    from orb import Query as Q, QueryGroup

    a = Q('username') != 'bob'
    b = Q('username') != 'tom'
    c = a & b

    assert type(c) is QueryGroup
    assert c.op is QueryGroup.Op.And
    assert c.queries[0] is a
    assert c.queries[1] is b


def test_query_or_joining_two_query_objects():
    """Test OR joining two query objects."""
    from orb import Query as Q, QueryGroup

    a = Q('username') != 'bob'
    b = Q('username') != 'tom'
    c = a | b

    assert type(c) is QueryGroup
    assert c.op is QueryGroup.Op.Or
    assert c.queries[0] is a
    assert c.queries[1] is b


def test_query_joining_an_empty_query_object():
    """Test AND / OR joining an empty query object."""
    from orb import Query as Q

    a = Q('username') != 'bob'
    b = Q()
    c = a & b
    d = a | b

    assert c is a
    assert d is a


def test_query_and_joining_query_object_into_group():
    """Test AND joining a query object into a group."""
    from orb import Query as Q, QueryGroup

    a = Q('username') != 'bob'
    b = Q('username') != 'tom'
    c = Q('username') != 'sam'
    d = a & b & c
    e = (a & b) & c
    f = a & (b & c)
    g = (a & b) & (b & c)

    for x in (d, e, f):
        assert type(x) is QueryGroup
        assert x.op is QueryGroup.Op.And
        assert x.queries[0] is a
        assert x.queries[1] is b
        assert x.queries[2] is c

    assert g.op is QueryGroup.Op.And
    assert g.queries[0] is a
    assert g.queries[1] is b
    assert g.queries[2] is b
    assert g.queries[3] is c


def test_query_or_joining_query_object_into_group():
    """Test AND joining a query object into a group."""
    from orb import Query as Q, QueryGroup

    a = Q('username') != 'bob'
    b = Q('username') != 'tom'
    c = Q('username') != 'sam'
    d = a | b | c
    e = (a | b) | c
    f = a | (b | c)
    g = (a | b) | (b | c)

    for x in (d, e, f):
        assert type(x) is QueryGroup
        assert x.op is QueryGroup.Op.Or
        assert x.queries[0] is a
        assert x.queries[1] is b
        assert x.queries[2] is c

    assert g.op is QueryGroup.Op.Or
    assert g.queries[0] is a
    assert g.queries[1] is b
    assert g.queries[2] is b
    assert g.queries[3] is c


def test_query_nesting():
    """Test AND joining a query object into a group."""
    from orb import Query as Q, QueryGroup

    a = Q('username') != 'bob'
    b = Q('username') != 'tom'
    c = Q('username') != 'sam'
    d = (a | b) & c
    e = a | (b & c)
    f = (a | b) & (a | c)
    g = (a & b) | (a & c)

    assert d.op is QueryGroup.Op.And
    assert type(d.queries[0]) is QueryGroup
    assert d.queries[0].op is QueryGroup.Op.Or
    assert d.queries[0].queries[0] is a
    assert d.queries[0].queries[1] is b
    assert d.queries[1] is c

    assert e.op is QueryGroup.Op.Or
    assert e.queries[0] is a
    assert type(e.queries[1]) is QueryGroup
    assert e.queries[1].queries[0] is b
    assert e.queries[1].queries[1] is c

    assert f.op is QueryGroup.Op.And
    assert f.queries[0].op is QueryGroup.Op.Or
    assert f.queries[1].op is QueryGroup.Op.Or
    assert f.queries[0].queries[0] is a
    assert f.queries[0].queries[1] is b
    assert f.queries[1].queries[0] is a
    assert f.queries[1].queries[1] is c

    assert g.op is QueryGroup.Op.Or
    assert g.queries[0].op is QueryGroup.Op.And
    assert g.queries[1].op is QueryGroup.Op.And
    assert g.queries[0].queries[0] is a
    assert g.queries[0].queries[1] is b
    assert g.queries[1].queries[0] is a
    assert g.queries[1].queries[1] is c


def test_query_joining_with_blanks():
    """Test joining queries together with blank entries."""
    from orb import Query as Q

    a = Q() & (Q('username') == 'bob')
    b = (Q('username') == 'bob') & Q()

    assert type(a) is Q
    assert a.name == 'username'
    assert a.value == 'bob'
    assert type(b) is Q
    assert b.name == 'username'
    assert b.value == 'bob'


def test_query_joining_with_none():
    """Test joining queries with None."""
    from orb import Query as Q

    a = Q('username') == 'bob'
    b = a & None

    assert b is a

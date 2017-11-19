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

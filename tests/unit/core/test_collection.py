"""Tests for the Collection class."""
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('records,expected_count', (
    ([], 0),
    ([1, 2], 2),
))
async def test_collection_counter(records, expected_count):
    """Test counter function."""
    from orb import Collection

    coll = Collection(records=records)
    count = await coll.get_count()
    length = len(coll)

    assert count == length == expected_count


@pytest.mark.asyncio
async def test_collection_counter_wihout_store():
    """Test for raising error with empty collection."""
    from orb import Collection
    from orb.exceptions import StoreNotFound

    coll = Collection(records=None)
    with pytest.raises(StoreNotFound):
        await coll.get_count()


@pytest.mark.asyncio
async def test_collection_getter():
    """Test collection getter method."""
    from orb import Collection

    c = Collection(records=[1, 2, 3])
    assert await c.get('first') is 1
    assert await c.get('count') is 3
    assert await c.get('last') is 3


@pytest.mark.asyncio
async def test_collection_nested_getter():
    """Test collection nested getter."""
    from orb import Model, Collector, Field

    class User(Model):
        username = Field()
        employees = Collector(model='User')

    coll = User.__schema__.collectors['employees']
    c = coll.get_collection([User(values={'username': 'bob'})])
    assert await c.get('first.username') == 'bob'


@pytest.mark.asyncio
@pytest.mark.parametrize('records', (
    [],
))
async def test_collection_with_empty_records(records):
    """Test responses for an empty collection with defined records."""
    from orb import Collection

    c = Collection(records=records)
    assert len(c) == 0
    assert await c.get('first') is None
    assert await c.get('last') is None
    assert await c.get('username') == []


@pytest.mark.asyncio
async def test_collection_setting_values():
    """Test setting record values."""
    from orb import Model, Field, Collection

    class User(Model):
        username = Field()

    coll = Collection(records=[
        User(values={'username': 'bob'}),
        User(values={'username': 'john'})
    ])

    assert await coll.get('username') == ['bob', 'john']
    await coll.set('username', 'tom')
    assert await coll.get('username') == ['tom', 'tom']
    await coll.set('username', ['jack', 'jill'])
    assert await coll.get('username') == ['jack', 'jill']


@pytest.mark.asyncio
async def test_collection_setting_nested_values():
    """Test setting record values."""
    from orb import Model, Field, Collection

    class User(Model):
        username = Field()
        manager = Field()

    u = User(values={'username': 'bill'})
    coll = Collection(records=[
        User(values={'username': 'bob', 'manager': u}),
        User(values={'username': 'john', 'manager': u})
    ])

    assert await coll.get('manager.username') == ['bill', 'bill']
    await coll.set('manager.username', 'tom')
    assert await coll.get('manager.username') == ['tom', 'tom']


@pytest.mark.asyncio
@pytest.mark.parametrize('key', (
    'count',
    'first',
    'last',
))
async def test_collection_setting_reserved_words_fail(key):
    """Test attempting to set reserved words raises a ReadOnly error."""
    from orb import Collection
    from orb.exceptions import ReadOnly

    c = Collection()
    with pytest.raises(ReadOnly):
        await c.set(key, 1)


@pytest.mark.asyncio
async def test_collection_delete():
    """Test deleting record from store."""
    from orb import Collection, Store

    class Test:
        async def delete_collection(self, collection, context):
            return len(collection)

    store = Store(backend=Test())
    coll = Collection(records=[1, 2, 3], store=store)

    assert await coll.delete() == 3


@pytest.mark.asyncio
async def test_collection_save():
    """Test saving record from a store."""
    from orb import Collection, Store

    class Test:
        async def save_collection(self, collection, context):
            return []

    store = Store(backend=Test())
    coll = Collection(records=[1, 2, 3], store=store)

    assert await coll.save() == []


def test_collection_refining():
    """Test refining a collection down by merging contexts."""
    from orb import Collection, make_context, Query as Q

    q = Q('active') == True  # noqa: E712
    coll = Collection(context=make_context(where=q))
    assert coll.context.where.name == 'active'
    assert coll.context.where.value is True

    q2 = Q('username') == 'bob'
    coll2 = coll.refine(where=q2)
    assert coll.context.where.name == 'active'
    assert coll2.context.where.queries[0].name == 'username'
    assert coll2.context.where.queries[0].value == 'bob'
    assert coll2.context.where.queries[1] is coll.context.where


@pytest.mark.asyncio
async def test_collection_slicing():
    """Test slicing a collection will update context."""
    from orb import Collection

    coll = Collection(records=[1, 2, 3])
    assert await coll[1:2].get_records() == [2]
    assert await coll[1:].get_records() == [2, 3]
    assert await coll[:1].get_records() == [1]

    coll2 = Collection()
    full_slice = coll2[1:2]
    left_slice = coll2[1:]
    right_slice = coll2[:2]

    assert full_slice.context.start == 1
    assert full_slice.context.limit == 1
    assert left_slice.context.start == 1
    assert left_slice.context.limit is None
    assert right_slice.context.start is None
    assert right_slice.context.limit == 2

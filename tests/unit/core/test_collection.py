"""Tests for the Collection class."""
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('records,expected_count', (
    (None, 0),
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
    None,
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
        async def delete_collection(self, collection):
            return len(collection)

    store = Store(backend=Test())
    coll = Collection(records=[1, 2, 3], store=store)

    assert await coll.delete() == 3


@pytest.mark.asyncio
async def test_collection_save():
    """Test saving record from a store."""
    from orb import Collection, Store

    class Test:
        async def save_collection(self, collection):
            return []

    store = Store(backend=Test())
    coll = Collection(records=[1, 2, 3], store=store)

    assert await coll.save() == []

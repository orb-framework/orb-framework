"""Tests for the Collector class."""
import pytest


def test_collector_definition():
    """Test defining collector."""
    from orb import Collector

    c = Collector(name='users')
    assert c.name == 'users'
    assert c.model is None
    assert c.get_collection().model is None


def test_collector_model_reference():
    """Test collector properly references a model."""
    from orb import Model, Collector

    class CollectorModelReference(Model):
        pass

    c = Collector(name='users', model='CollectorModelReference')
    assert c.model is CollectorModelReference
    assert c.get_collection().model is CollectorModelReference


def test_collector_initialize_collection():
    """Test collector returns collection instance."""
    from orb import Collector, Collection

    c = Collector()
    coll = Collection()
    assert c.get_collection(coll) is coll


@pytest.mark.asyncio
async def test_collector_by_record():
    """Test collector by record method."""
    from orb import Model, Collector

    class CollectorRecordModel(Model):
        employees = Collector(model='CollectorRecordModel')

    u = CollectorRecordModel()
    coll = await u.get('employees')
    assert coll.source is u
    assert coll.model is CollectorRecordModel


@pytest.mark.asyncio
async def test_collector_with_getter():
    """Test collector with custom getter."""
    from orb import Model, Collector, Collection

    class User(Model):
        employees = Collector(model='User')

        @employees.getter
        async def get_employees(self):
            return Collection(records=[self], source=self)

    u = User()
    coll = await u.get('employees')
    assert coll.source is u
    assert len(coll) == 1
    assert await coll.get_first() is u


@pytest.mark.asyncio
async def test_collector_with_setter():
    """Test collector with custom setter."""
    from orb import Model, Collector

    class User(Model):
        employees = Collector(model='User')

        @employees.setter
        async def set_employees(self, collection):
            self.employees = collection

    u = User()
    records = [1, 2, 3]
    await u.set('employees', records)
    assert u.employees is records


@pytest.mark.asyncio
async def test_collector_with_query():
    """Test collector with custom query."""
    from orb import Model, Collector

    class User(Model):
        employees = Collector(model='User')

        @employees.query
        async def query_employees(self, q):
            return 'query'

    u = User()
    r = await u.__schema__.collectors['employees'].querymethod(u, None)
    assert r == 'query'

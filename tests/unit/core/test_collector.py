"""Tests for the Collector class."""
import pytest


def test_collector_definition():
    """Test defining collector."""
    from orb import Collector

    c = Collector(name='users')
    assert c.name == 'users'
    assert c.model is None
    assert c.make_collection().model is None


def test_collector_model_reference():
    """Test collector properly references a model."""
    from orb import Model, Collector

    class CollectorModelReference(Model):
        pass

    c = Collector(name='users', model='CollectorModelReference')
    assert c.model is CollectorModelReference
    assert c.make_collection().model is CollectorModelReference


def test_collector_initialize_collection():
    """Test collector returns collection instance."""
    from orb import Collector, Collection

    c = Collector()
    coll = Collection()
    assert c.make_collection(records=coll) is coll


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


def test_collector_reverse_lookup():
    """Test reverse lookup definition for a collector."""
    from orb import Model, Collector, Field

    class Page(Model):
        id = Field(flags={'Key'})
        parent_id = Field(refers_to='Page.id')
        children = Collector(model='Page', source='parent_id')

    page_schema = Page.__schema__

    assert page_schema['parent_id'].refers_to_model is Page
    assert page_schema['parent_id'].refers_to_field.name == 'id'
    assert page_schema['children'].model is Page
    assert page_schema['children'].source_field.name == 'parent_id'
    assert page_schema['children'].target_field is None
    assert page_schema['children'].through_model is None


def test_collector_pipe():
    """Test collector definition with pipe record."""
    from orb import Model, Collector, Index, Field

    class Page(Model):
        id = Field(flags={'Key'})

        categories = Collector(
            model='Category',
            source='page_id',
            target='category_id',
            through='PageCategory'
        )

    class PageCategory(Model):
        page_id = Field(refers_to='Page.id')
        category_id = Field(refers_to='Category.id')

        by_page_and_category = Index(
            field_names=['page_id', 'category_id'],
            flags={'Key'}
        )

    class Category(Model):
        id = Field(flags={'Key'})

        pages = Collector(
            model='Page',
            source='category_id',
            target='page_id',
            through='PageCategory'
        )

    page_schema = Page.__schema__
    pc_schema = PageCategory.__schema__
    cat_schema = Category.__schema__

    assert page_schema['categories'].model is Category
    assert page_schema['categories'].source_field.name == 'page_id'
    assert page_schema['categories'].target_field.name == 'category_id'
    assert page_schema['categories'].through_model is PageCategory

    assert pc_schema['page_id'].refers_to_model is Page
    assert pc_schema['page_id'].refers_to_field.name == 'id'
    assert pc_schema['category_id'].refers_to_model is Category
    assert pc_schema['category_id'].refers_to_field.name == 'id'

    assert cat_schema['pages'].model is Page
    assert cat_schema['pages'].source_field.name == 'category_id'
    assert cat_schema['pages'].target_field.name == 'page_id'
    assert cat_schema['pages'].through_model is PageCategory


@pytest.mark.asyncio
async def test_collector_reverse_lookup_collection_context():
    """Test to validate a proper context is generated for a lookup."""
    from orb import Model, Collector, Field, Query

    class Page(Model):
        id = Field(flags={'Key'})
        parent_id = Field(refers_to='Page.id')
        children = Collector(model='Page', source='parent_id')

    page = Page(state={'id': 1})
    children = await page.get('children')

    assert children.model is Page
    assert children.context.where is not None
    assert children.context.where.model is Page
    assert children.context.where.name is 'parent_id'
    assert children.context.where.op is Query.Op.Is
    assert children.context.where.value is page

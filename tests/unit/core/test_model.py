"""Model class tests."""
import pytest


def test_model_definition():
    """Test the User model has a schema object."""
    from orb import Model, Field

    class User(Model):
        id = Field()

    assert User.__schema__ is not None


def test_model_definition_with_mixins():
    """Test defining a model that uses a mixin."""
    from orb import Model, Field, Collector, Index

    class CreationMixin:
        created_by = Field()
        created_at = Field()

        creations = Collector()
        by_created_by = Index()

    class UpdateMixin:
        updated_by = Field()
        updated_at = Field()

    class Page(CreationMixin, UpdateMixin, Model):
        text = Field()

    class Comment(CreationMixin, UpdateMixin, Model):
        text = Field()

    p_schema = Page.__schema__
    c_schema = Comment.__schema__

    assert len(p_schema.local_collectors) == 1
    assert len(p_schema.local_indexes) == 1
    assert len(p_schema.local_fields) == 5
    assert len(c_schema.local_fields) == 5

    assert p_schema.fields['created_by'] is c_schema.fields['created_by']
    assert p_schema.fields['updated_by'] is c_schema.fields['updated_by']
    assert p_schema.fields['text'] is not c_schema.fields['created_by']


def test_model_definition_with_inheritance():
    """Test defining a model that uses inheritance."""
    from orb import Model, Field, Collector, Index

    class User(Model):
        id = Field()
        username = Field()
        password = Field()

        login_attempts = Collector()

        by_username = Index()

    class Employee(User):
        badge = Field()
        manager = Field()

    u_schema = User.__schema__
    e_schema = Employee.__schema__

    assert len(u_schema.local_fields) == 3
    assert len(u_schema.fields) == 3
    assert len(u_schema.local_collectors) == 1
    assert len(u_schema.collectors) == 1
    assert len(u_schema.local_indexes) == 1
    assert len(u_schema.indexes) == 1
    assert len(e_schema.local_fields) == 2
    assert len(e_schema.fields) == 5
    assert len(e_schema.local_collectors) == 0
    assert len(e_schema.collectors) == 1
    assert len(e_schema.local_indexes) == 0
    assert len(e_schema.indexes) == 1

    assert e_schema.fields['id'] is u_schema.fields['id']


def test_model_definition_with_abstraction():
    """Test defining a model with an abstract base class."""
    from orb import Model, Field

    class AbstractUser(Model):
        __abstract__ = True

        id = Field()
        username = Field()
        password = Field()

    class Account(AbstractUser):
        badge = Field()

    class Employee(AbstractUser):
        badge = Field()
        manager = Field()

    u_schema = AbstractUser.__schema__
    a_schema = Account.__schema__
    e_schema = Employee.__schema__

    assert u_schema is None
    assert a_schema is not None
    assert e_schema is not None

    assert len(e_schema.local_fields) == 5
    assert len(e_schema.fields) == 5
    assert len(a_schema.local_fields) == 4
    assert len(a_schema.local_fields) == 4

    assert e_schema.fields['id'] is a_schema.fields['id']
    assert e_schema.fields['badge'] is not a_schema.fields['badge']


@pytest.mark.asyncio
async def test_model_definition_with_getters():
    """Test a model with custom field getters."""
    from orb import Model, Field

    class User(Model):
        id = Field()
        first_name = Field()
        last_name = Field()
        display_name = Field(flags=Field.Flags.Virtual)

        @display_name.getter
        async def get_display_name(self):
            values = await self.gather('first_name', 'last_name')
            return '{} {}'.format(*values)

    u = User(values={'first_name': 'John', 'last_name': 'Doe'})
    assert await u.get('display_name') == 'John Doe'


@pytest.mark.asyncio
async def test_model_definition_with_virtual_decorator():
    """Test a model with custom field getters."""
    from orb import Collector, Collection, Model, Field, virtual

    class User(Model):
        id = Field()
        first_name = Field()
        last_name = Field()

        @virtual(Field)
        async def display_name(self):
            values = await self.gather('first_name', 'last_name')
            return '{} {}'.format(*values)

        @virtual(Collector)
        async def groups(self):
            return Collection()

    u = User(values={'first_name': 'John', 'last_name': 'Doe'})
    assert await u.get('display_name') == 'John Doe'
    assert await u.get('groups.count') == 0


@pytest.mark.asyncio
async def test_model_initialization_with_values():
    """Test model creation using values."""
    from orb import Model, Field

    class User(Model):
        id = Field()
        username = Field()

    user = User(values={'id': 1, 'username': 'bob'})
    assert await user.gather('id', 'username') == [1, 'bob']
    assert user.local_changes == {
        'id': (None, 1),
        'username': (None, 'bob')
    }
    user.mark_loaded()
    assert await user.gather('id', 'username') == [1, 'bob']
    assert user.local_changes == {}


@pytest.mark.asyncio
async def test_model_initialization_with_state():
    """Test model initialization with state."""
    from orb import Model, Field

    class User(Model):
        id = Field()
        username = Field()

    user = User(state={'id': 1, 'username': 'bob'})
    assert await user.gather('id', 'username') == [1, 'bob']
    assert user.local_changes == {}


@pytest.mark.asyncio
async def test_model_initialization_with_nested_values():
    """Test model initialization with nested values."""
    from orb import Model, Field

    class User(Model):
        id = Field()
        username = Field()
        manager = Field()

    bob = User(values={'username': 'bob'})
    tom = User(values={'username': 'tom', 'manager': bob})

    assert await tom.get('manager.username') == 'bob'


@pytest.mark.asyncio
async def test_model_initialization_with_nested_state():
    """Test model initialization with nested values."""
    from orb import Model, Field

    class User(Model):
        id = Field()
        username = Field()
        manager = Field()

    bob = User(state={'username': 'bob'})
    tom = User(state={'username': 'tom', 'manager': bob})

    assert await tom.get('manager.username') == 'bob'


@pytest.mark.asyncio
async def test_model_initialization_with_nested_collections_by_state():
    """Test model initialization with nested values."""
    from orb import Model, Field, Collector

    class User(Model):
        id = Field()
        username = Field()
        employees = Collector(model='User')

    user = User(state={
        'id': 1,
        'username': 'bob',
        'employees': [{
            'id': 2,
            'username': 'tom'
        }, {
            'id': 3,
            'username': 'john'
        }]
    })

    assert await user.get('employees.count') == 2
    assert set(await user.get('employees.username')) == {'tom', 'john'}


@pytest.mark.asyncio
async def test_model_initialization_with_nested_collections_by_values():
    """Test model initialization with nested values."""
    from orb import Model, Field, Collector

    class User(Model):
        id = Field()
        username = Field()
        employees = Collector(model='User')

    user = User(values={
        'id': 1,
        'username': 'bob',
        'employees': [{
            'id': 2,
            'username': 'tom'
        }, {
            'id': 3,
            'username': 'john'
        }]
    })

    assert await user.get('employees.count') == 2
    assert set(await user.get('employees.username')) == {'tom', 'john'}


def test_model_searching():
    """Test searching model for others by name."""
    from orb import Model

    class A(Model):
        pass

    class B(Model):
        pass

    class C(A):
        pass

    assert Model.find_model('A') is A
    assert Model.find_model('B') is B
    assert Model.find_model('C') is C
    assert A.find_model('B') is None
    assert A.find_model('C') is C


@pytest.mark.asyncio
async def test_model_get_value(make_users):
    """Test getting simple values work."""
    bob = make_users('bob')

    assert await bob.get('id') == 1
    assert await bob.get_value('id') == 1

    with pytest.raises(KeyError):
        assert await bob.get('id2') is None
    with pytest.raises(KeyError):
        assert await bob.get_value('id2') is None


@pytest.mark.asyncio
async def test_model_gather_values(make_users):
    """Test gathering multiple values at one time."""
    bob = make_users('bob')
    assert await bob.gather('id', 'username') == [1, 'bob']


@pytest.mark.asyncio
async def test_model_get_nested_value(make_users):
    """Test getting nested properties."""
    john, jane = make_users('john', 'jane')
    await john.set('manager', jane)
    assert await john.get('manager.username') == 'jane'


@pytest.mark.asyncio
async def test_model_gather_nested_values(make_users):
    """Test gathering multiple values which can be nested."""
    john, jane = make_users('john', 'jane')
    await john.set('manager', jane)
    result = await john.gather('username', 'manager.username')
    assert result == ['john', 'jane']


@pytest.mark.asyncio
async def test_model_modification(make_users):
    """Test modifying records."""
    bob = make_users('bob')
    assert await bob.get('username') == 'bob'
    await bob.set('username', 'tom')
    assert await bob.get('username') == 'tom'
    assert bob.local_changes == {'username': ('bob', 'tom')}


@pytest.mark.asyncio
async def test_model_modification_reset(make_users):
    """Test resetting record clears changes."""
    bob = make_users('bob')
    assert await bob.get('username') == 'bob'
    await bob.set('username', 'tom')
    assert await bob.get('username') == 'tom'
    assert bob.local_changes == {'username': ('bob', 'tom')}
    await bob.reset()
    assert bob.local_changes == {}


@pytest.mark.asyncio
async def test_model_modification_reset_by_change(make_users):
    """Test resetting record clears changes."""
    bob = make_users('bob')
    assert await bob.get('username') == 'bob'
    await bob.set('username', 'tom')
    assert await bob.get('username') == 'tom'
    assert bob.local_changes == {'username': ('bob', 'tom')}
    await bob.set('username', 'bob')
    assert bob.local_changes == {}


@pytest.mark.asyncio
async def test_model_modification_by_update(make_users):
    """Test update modifies multiple fields."""
    bob = make_users('bob')
    assert await bob.gather('id', 'username') == [1, 'bob']
    await bob.update({'id': 2, 'username': 'tom'})
    assert await bob.gather('id', 'username') == [2, 'tom']


@pytest.mark.asyncio
async def test_model_set_collection():
    """Test assigning a value to a collection."""
    from orb import Model, Field

    class User(Model):
        employees = Field()

    u = User()
    await u.set('employees', [1, 2, 3])
    assert await u.get('employees') == [1, 2, 3]


@pytest.mark.asyncio
async def test_model_modification_with_nesting(make_users):
    """Test update nested properties."""
    bob, sam = make_users('bob', 'sam')
    await bob.set('manager', sam)
    assert await bob.get('manager.username') == 'sam'
    await bob.set('manager.username', 'sammy')
    assert await bob.get('manager.username') == 'sammy'
    assert await sam.get('username') == 'sammy'


@pytest.mark.asyncio
async def test_model_modification_with_custom_setter():
    """Test update with custom setter method."""
    from orb import Model, Field, virtual

    class User(Model):
        first_name = Field()
        last_name = Field()

        @virtual(Field)
        async def display_name(self):
            first_name, last_name = await self.gather(
                'first_name',
                'last_name'
            )
            return '{} {}'.format(first_name, last_name)

        @display_name.setter
        async def set_display_name(self, name):
            first_name, _, last_name = name.partition(' ')
            await self.set('first_name', first_name)
            await self.set('last_name', last_name)

    u = User(values={'first_name': 'John', 'last_name': 'Smith'})
    assert await u.get('display_name') == 'John Smith'
    await u.set('display_name', 'Jane Doe')
    assert await u.get('display_name') == 'Jane Doe'
    assert set(u.local_changes.keys()) == {'first_name', 'last_name'}


@pytest.mark.asyncio
async def test_model_save():
    """Test saving a model."""
    from orb import Model, Field, Store

    class Test:
        async def save_record(self, record: Model) -> str:
            return {'id': 1}

    store = Store(backend=Test())

    class User(Model):
        id = Field()
        username = Field()
        password = Field()

    u = User(values={'username': 'bob'}, store=store)
    assert await u.save() is True
    assert await u.gather('id', 'username') == [1, 'bob']


@pytest.mark.asyncio
async def test_model_save_without_modification():
    """Test save without modifications."""
    from orb import Model, Field, Store

    class Test:
        async def save_record(self, record: Model) -> str:
            return {'id': 1}

    store = Store(backend=Test())

    class User(Model):
        id = Field()
        username = Field()

    u = User(state={'username': 'bob'}, store=store)
    assert await u.save() is False
    await u.set('username', 'tom')
    assert await u.save() is True
    assert await u.gather('id', 'username') == [1, 'tom']


@pytest.mark.asyncio
async def test_model_save_read_only():
    """Test saving read-only models raises an error."""
    from orb import Model
    from orb.exceptions import ReadOnly

    class UserView(Model):
        __view__ = True

    u = UserView()
    with pytest.raises(ReadOnly):
        await u.save()


@pytest.mark.asyncio
async def test_model_delete():
    """Test deleting a model."""
    from orb import Model, Store

    class Test:
        async def delete_record(self, record: Model) -> str:
            return 'deleted'

    store = Store(backend=Test())

    class User(Model):
        pass

    u = User(store=store)
    assert await u.delete() == 'deleted'


@pytest.mark.asyncio
async def test_model_delete_read_only():
    """Test saving read-only models raises an error."""
    from orb import Model
    from orb.exceptions import ReadOnly

    class UserView(Model):
        __view__ = True

    u = UserView()
    with pytest.raises(ReadOnly):
        await u.delete()


@pytest.mark.asyncio
async def test_model_create():
    """Test creating a new model."""
    from orb import Model, Field, Store

    class Test:
        async def save_record(self, record: Model) -> str:
            return {'id': 1}

    store = Store(backend=Test())

    class User(Model):
        id = Field()
        username = Field()
        password = Field()

    user = await User.create({'username': 'jdoe'}, store=store)
    assert await user.gather('id', 'username') == [1, 'jdoe']


@pytest.mark.asyncio
async def test_model_create_view_read_only():
    """Test creating a new model."""
    from orb import Model
    from orb.exceptions import ReadOnly

    class UserView(Model):
        __view__ = True

    with pytest.raises(ReadOnly):
        await UserView.create({'username': 'jdoe'})


def test_model_select_collection():
    """Test selecting a collection from a model."""
    from orb import Model, Field, Query as Q

    class User(Model):
        id = Field()

    coll = User.select(where=Q('id') == 1)

    assert coll.model is User
    assert coll.context.where.name == 'id'
    assert coll.context.where.value == 1

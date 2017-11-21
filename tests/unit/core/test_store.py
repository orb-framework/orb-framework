"""Tests for the Store class."""
import pytest


@pytest.mark.asyncio
async def test_store_without_backend():
    """Test creating a store without a backend."""
    from orb import Store

    store = Store()
    with pytest.raises(RuntimeError):
        await store.save_record(None, None)

    with pytest.raises(RuntimeError):
        await store.save_collection(None, None)

    with pytest.raises(RuntimeError):
        await store.delete_record(None, None)

    with pytest.raises(RuntimeError):
        await store.delete_collection(None, None)


def test_store_stack():
    """Test store stack creation."""
    from orb import Store, current_store

    store = Store()

    assert current_store() is None
    with store:
        assert current_store() is store
    assert current_store() is None


def test_store_stack_for_context():
    """Test store stack with context usage."""
    from orb import Store, Model

    store = Store()

    class User(Model):
        pass

    u = User()
    assert u.context.store is None
    with store:
        assert u.context.store is store
    assert u.context.store is None


def test_store_with_name():
    """Test store with naming context usage."""
    from orb import Store, Model

    class User(Model):
        __store__ = 'auth'

    class Book(Model):
        __store__ = 'content'

    auth = Store(name='auth')
    content = Store(name='content')

    u = User()
    b = Book()

    assert u.context.store is None
    assert b.context.store is None
    with auth, content:
        assert u.context.store is auth
        assert b.context.store is content
    with content:
        assert u.context.store is None
        assert b.context.store is content
    with auth:
        assert u.context.store is auth
        assert b.context.store is None
    assert u.context.store is None
    assert b.context.store is None


def test_store_with_global_reference():
    """Test store with global context registry."""
    from orb import Store, Model, push_store, pop_store

    class User(Model):
        __store__ = 'auth'

    class Book(Model):
        __store__ = 'content'

    auth = Store(name='auth')
    content = Store(name='content')

    push_store(auth)
    push_store(content)

    u = User()
    b = Book()

    assert u.context.store is auth
    assert b.context.store is content

    assert pop_store() is content
    assert pop_store() is auth
    assert pop_store() is None
    assert pop_store(auth) is None

    assert u.context.store is None
    assert b.context.store is None


def test_store_with_context_override():
    """Test setting store with a context override."""
    from orb import Store, Model, push_store, pop_store

    class User(Model):
        __store__ = 'auth'

    auth = Store(name='auth')
    content = Store(name='content')

    push_store(auth)

    a = User()
    b = User(store=content)

    assert a.context.store is auth
    assert b.context.store is content

    a.context.store = content

    assert a.context.store is content
    assert b.context.store is content

    c = User()

    assert c.context.store is auth

    pop_store()


def test_store_backend_is_abstract():
    """Test to ensure that the backend class type is abstract."""
    from orb.core.store_backend import StoreBackend

    with pytest.raises(TypeError):
        StoreBackend()

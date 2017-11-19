"""Tests for the Store class."""
import pytest


def test_store_model_registry():
    """Test creating a model with a store association."""
    from orb import Store, Model

    store = Store()

    class User(Model):
        __store__ = store

    assert User.__store__ is store
    assert store.models['User'] is User


def test_store_add_model():
    """Test adding a model to a store."""
    from orb import Store, Model

    class User(Model):
        pass

    store = Store()
    store.register(User)

    assert User.__store__ is store
    assert store.models['User'] is User


def test_store_decorator():
    """Test adding a model to a store via decorator."""
    from orb import Store, Model

    store = Store()

    @store.register
    class User(Model):
        pass

    assert User.__store__ is store
    assert store.models['User'] is User


@pytest.mark.asyncio
async def test_store_without_backend():
    """Test creating a store without a backend."""
    from orb import Store

    store = Store()
    with pytest.raises(RuntimeError):
        await store.save_record(None)

    with pytest.raises(RuntimeError):
        await store.save_collection(None)

    with pytest.raises(RuntimeError):
        await store.delete_record(None)

    with pytest.raises(RuntimeError):
        await store.delete_collection(None)

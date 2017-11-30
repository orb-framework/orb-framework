"""Define Store class."""

from typing import List, Type

from ..exceptions import StoreNotFound

STORE_STACK = []


class Store:
    """Define backend storage for models."""

    def __init__(
        self,
        name: str='',
        namespace: str='',
        backend: 'StoreBackend'=None
    ):
        self.backend = backend
        self.name = name
        self.namespace = namespace

    def __enter__(self):
        """Push this store onto the top of the stack."""
        push_store(self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Pop this store off the top of the stack."""
        pop_store(self)

    async def delete_record(self, record: 'Model', context: 'Context') -> int:
        """Delete the record from the store."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return await self.backend.delete_record(record, context)

    async def delete_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> int:
        """Delete the collection from the backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return await self.backend.delete_collection(collection, context)

    async def get_count(self, model: Type['Model'], context: 'Context') -> int:
        """Return a count of the records given a model and search context."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return await self.backend.get_count(model, context)

    async def get_records(
        self,
        model: Type['Model'],
        context: 'Context'
    ) -> List[dict]:
        """Get records from the store based on the given context."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return await self.backend.get_records(model, context)

    async def save_record(self, record: 'Model', context: 'Context') -> dict:
        """Save the record to the store backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return await self.backend.save_record(record, context)

    async def save_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> list:
        """Save the collection to the store backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return await self.backend.save_collection(collection, context)


def current_store(name: str=None) -> Store:
    """Return the current active store."""
    if not name:
        try:
            return STORE_STACK[-1]
        except IndexError:
            raise StoreNotFound()

    for store in STORE_STACK:
        if store.name == name:
            return store
    else:
        raise StoreNotFound()


def push_store(store: Store) -> Store:
    """Push the store instance to the top of the stack."""
    STORE_STACK.append(store)
    return store


def pop_store(store: Store=None) -> Store:
    """Pop the store instance from the end of the stack."""
    if store is not None:
        try:
            STORE_STACK.remove(store)
            return store
        except ValueError:
            return None
    else:
        try:
            return STORE_STACK.pop()
        except IndexError:
            return None

"""Define Store class."""

STORE_STACK = []


class Store:
    """Define backend storage for models."""

    def __init__(self, name: str='', backend=None):
        self.backend = backend
        self.name = name

    def __enter__(self):
        """Push this store onto the top of the stack."""
        push_store(self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Pop this store off the top of the stack."""
        pop_store(self)

    def delete_record(self, record: 'Model') -> int:
        """Delete the record from the store."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.delete_record(record)

    def delete_collection(self, collection: 'Collection') -> int:
        """Delete the collection from the backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.delete_collection(collection)

    def save_record(self, record: 'Model') -> dict:
        """Save the record to the store backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.save_record(record)

    def save_collection(self, collection: 'Collection') -> list:
        """Save the collection to the store backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.save_collection(collection)


def current_store(name: str=None) -> Store:
    """Return the current active store."""
    if not name:
        try:
            return STORE_STACK[-1]
        except IndexError:
            return None
    for store in STORE_STACK:
        if store.name == name:
            return store
    return None


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

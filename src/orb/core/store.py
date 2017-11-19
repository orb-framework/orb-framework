"""Define Store class."""

from typing import Type

from .collection import Collection
from .model import Model


class Store:
    """Define backend storage for models."""

    def __init__(self, backend=None):
        self.backend = backend
        self.models = {}

    def delete_record(self, record: Model) -> int:
        """Delete the record from the store."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.delete_record(record)

    def delete_collection(self, collection: Collection) -> int:
        """Delete the collection from the backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.delete_collection(collection)

    def register(self, model: Type[Model]):
        """Associate given model to this store."""
        self.models[model.__name__] = model
        model.__store__ = self
        return model

    def save_record(self, record: Model) -> dict:
        """Save the record to the store backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.save_record(record)

    def save_collection(self, collection: Collection) -> list:
        """Save the collection to the store backend."""
        if self.backend is None:
            raise RuntimeError('Store requires backend.')
        return self.backend.save_collection(collection)

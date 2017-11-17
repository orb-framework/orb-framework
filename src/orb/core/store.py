"""Define Store class."""

from typing import Type

from .collection import Collection
from .model import Model


class Store:
    """Define backend storage for models."""

    def __init__(self, backend=None):
        self.backend = backend
        self.models = {}

    def add_model(self, model: Type[Model]):
        """Associate given model to this store."""
        self.models[model.__name__] = model
        model.__store__ = self

    def delete_record(self, record: Model) -> int:
        """Delete the record from the store."""
        return self.backend.delete_record(record)

    def delete_collection(self, collection: Collection) -> int:
        """Delete the collection from the backend."""
        return self.backend.delete_collection(collection)
